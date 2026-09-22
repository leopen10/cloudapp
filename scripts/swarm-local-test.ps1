# swarm-local-test.ps1
# Valide la pile de PRODUCTION (docker-compose.prod.yml) en la deployant reellement
# dans Docker Swarm sur votre PC (Docker Desktop), avec les images publiees sur Docker Hub.
#
# Deploiement et tests :
#   cd C:\Users\leoop\cloudapp
#   powershell -ExecutionPolicy Bypass -File scripts\swarm-local-test.ps1
#
# Arret et retour a la normale :
#   powershell -ExecutionPolicy Bypass -File scripts\swarm-local-test.ps1 -Down
#   (ajouter -PurgeVolumes pour effacer aussi les donnees de la pile de test)
#
# Les mots de passe sont generes au hasard et n'existent que dans ce script :
# aucune variable d'environnement ne reste dans votre fenetre PowerShell.
# La pile utilise le nom "cloudprod" : ses volumes sont distincts de ceux de docker-compose.test.yml.
# Ce fichier ne contient volontairement aucun accent, pour eviter les problemes d'encodage.

param(
    [switch]$Down,
    [switch]$PurgeVolumes,
    [string]$DockerUser = 'leonelpengou10',
    [string]$Tag = 'latest',
    [string]$Stack = 'cloudprod',
    [int]$TimeoutSec = 480
)

$ErrorActionPreference = 'Continue'

function Say {
    param([string]$Message, [string]$Color = 'White')
    Write-Host $Message -ForegroundColor $Color
}

function New-Password {
    param([int]$Length = 24)
    $chars = (48..57) + (65..90) + (97..122)
    return -join ($chars | Get-Random -Count $Length | ForEach-Object { [char]$_ })
}

function Test-DockerEngine {
    $v = docker info --format '{{.ServerVersion}}' 2>$null
    return ($LASTEXITCODE -eq 0 -and $v)
}

function Get-Retry {
    param([string]$Url, [int]$Tries = 25)
    for ($i = 1; $i -le $Tries; $i++) {
        try {
            return Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 5
        }
        catch {
            Start-Sleep -Seconds 3
        }
    }
    return $null
}

function Get-ServiceEnv {
    # Lit une variable d'environnement dans la definition d'un service Swarm (ou renvoie $null).
    param([string]$Service, [string]$Key)
    $json = docker service inspect $Service --format '{{json .Spec.TaskTemplate.ContainerSpec.Env}}' 2>$null
    if ($LASTEXITCODE -ne 0 -or -not $json -or $json -eq 'null') { return $null }
    try { $arr = $json | ConvertFrom-Json } catch { return $null }
    foreach ($e in @($arr)) {
        if ($e -like "$Key=*") { return $e.Substring($Key.Length + 1) }
    }
    return $null
}

$results = New-Object System.Collections.Generic.List[string]
function Add-Result {
    param([string]$Name, [bool]$Ok, [string]$Detail = '')
    $tag = 'FAIL'
    $color = 'Red'
    if ($Ok) { $tag = 'PASS'; $color = 'Green' }
    Say ("  [$tag] $Name $Detail") $color
    $results.Add("$tag|$Name")
}

$root = (Get-Location).Path
if (-not (Test-Path (Join-Path $root 'docker-compose.prod.yml'))) {
    Say 'ERREUR : lancez ce script depuis la racine du depot (le dossier qui contient docker-compose.prod.yml).' 'Red'
    Say ('Dossier actuel : ' + $root)
    exit 1
}

if (-not (Test-DockerEngine)) {
    Say 'ERREUR : le moteur Docker ne repond pas. Lancez Docker Desktop, attendez "Engine running", puis relancez.' 'Red'
    exit 1
}

# ---------------------------------------------------------------
# Mode arret
# ---------------------------------------------------------------
if ($Down) {
    Say ''
    Say '== Arret de la pile de production locale ==' 'Cyan'
    docker service update --quiet --publish-rm 16686 "${Stack}_jaeger" 2>$null | Out-Null
    docker stack rm $Stack
    Say 'Attente de la suppression des services (20 s)...'
    Start-Sleep -Seconds 20
    if ($PurgeVolumes) {
        foreach ($v in @("${Stack}_postgres_data", "${Stack}_grafana_data", "${Stack}_prometheus_data", "${Stack}_backup_data")) {
            docker volume inspect $v 2>$null | Out-Null
            if ($LASTEXITCODE -ne 0) {
                Say "Volume absent (rien a supprimer) : $v"
                continue
            }
            $removed = $false
            for ($i = 1; $i -le 12 -and -not $removed; $i++) {
                docker volume rm $v 2>$null | Out-Null
                if ($LASTEXITCODE -eq 0) { $removed = $true } else { Start-Sleep -Seconds 5 }
            }
            if ($removed) { Say "Volume supprime : $v" }
            else { Say "ATTENTION : volume non supprime (encore utilise ?) : $v" 'Yellow' }
        }
    }
    docker network rm traefik-public 2>$null | Out-Null
    $state = docker info --format '{{.Swarm.LocalNodeState}}'
    if ($state -eq 'active') {
        docker swarm leave --force | Out-Null
        Say 'Mode Swarm desactive.'
    }
    Say ''
    Say 'Termine. Pour reprendre le developpement : docker compose -f docker-compose.test.yml up -d' 'Cyan'
    exit 0
}

# ---------------------------------------------------------------
# 1) Preparation
# ---------------------------------------------------------------
Say ''
Say '== 1/4 Preparation ==' 'Cyan'

$existing = docker stack ls --format '{{.Name}}' 2>$null
$already = $false
foreach ($n in @($existing)) { if ($n -eq $Stack) { $already = $true } }

if (-not $already) {
    $busy = Get-NetTCPConnection -LocalPort 80 -State Listen -ErrorAction SilentlyContinue
    if ($busy) {
        Say 'ERREUR : le port 80 de votre PC est deja utilise (Traefik doit l''occuper).' 'Red'
        Say 'Programme concerne (numero de processus) :'
        $busy | Select-Object LocalAddress, OwningProcess | Format-Table | Out-String | Write-Host
        exit 1
    }
}

if (Test-Path (Join-Path $root 'docker-compose.test.yml')) {
    Say 'Arret de la pile de test (docker-compose.test.yml) pour liberer la memoire. Les donnees sont conservees.'
    docker compose -f docker-compose.test.yml down 2>$null | Out-Null
}

$swarmState = docker info --format '{{.Swarm.LocalNodeState}}'
if ($swarmState -ne 'active') {
    Say 'Activation du mode Swarm...'
    docker swarm init 2>&1 | Out-Null
    $swarmState = docker info --format '{{.Swarm.LocalNodeState}}'
    if ($swarmState -ne 'active') {
        Say 'ERREUR : docker swarm init a echoue. Essayez : docker swarm init --advertise-addr 127.0.0.1' 'Red'
        exit 1
    }
}
Say 'Mode Swarm actif.' 'Green'

$net = docker network ls --filter 'name=^traefik-public$' --format '{{.Name}}'
if (-not $net) {
    docker network create --driver overlay --attachable traefik-public | Out-Null
    Say 'Reseau traefik-public cree.'
}

# ---------------------------------------------------------------
# 2) Deploiement
# ---------------------------------------------------------------
Say ''
Say '== 2/4 Deploiement de la pile ==' 'Cyan'
try {
$env:DOCKER_USERNAME = $DockerUser
$env:IMAGE_TAG = $Tag
# Les volumes conservent le mot de passe PostgreSQL du premier deploiement : sur un redeploiement,
# on reutilise donc les secrets deja presents dans la pile au lieu d'en generer de nouveaux.
$pgPassword = $null
$jwtKey = $null
$grafanaPw = $null
if ($already) {
    $pgPassword = Get-ServiceEnv "${Stack}_postgres" 'POSTGRES_PASSWORD'
    $jwtKey = Get-ServiceEnv "${Stack}_auth" 'SECRET_KEY'
    $grafanaPw = Get-ServiceEnv "${Stack}_grafana" 'GF_SECURITY_ADMIN_PASSWORD'
    if ($pgPassword) { Say 'Pile existante : les mots de passe deja en place sont reutilises.' }
}
if (-not $pgPassword) { $pgPassword = New-Password 24 }
if (-not $jwtKey) { $jwtKey = New-Password 40 }
if (-not $grafanaPw) { $grafanaPw = New-Password 20 }
$env:POSTGRES_PASSWORD = $pgPassword
$env:JWT_SECRET_KEY = $jwtKey
$env:GRAFANA_ADMIN_PASSWORD = $grafanaPw
$env:RESEND_API_KEY = ''
$grafanaPassword = $env:GRAFANA_ADMIN_PASSWORD

docker stack deploy -c docker-compose.prod.yml $Stack
if ($LASTEXITCODE -ne 0) {
    Say 'ERREUR : le deploiement a echoue (voir le message ci-dessus).' 'Red'
    exit 1
}

# Jaeger n'est volontairement PAS publie dans docker-compose.prod.yml (un seul port public : 80,
# pour Traefik). On l'expose ici temporairement, en local seulement, pour pouvoir consulter les
# traces dans un navigateur pendant la validation/demo ; "-Down" retire cette exception.
docker service update --quiet --publish-add published=16686,target=16686,mode=host "${Stack}_jaeger" 2>$null | Out-Null

# ---------------------------------------------------------------
# 3) Attente des services
# ---------------------------------------------------------------
Say ''
Say '== 3/4 Attente des services (jusqu''a 8 minutes : telechargement des images) ==' 'Cyan'
$expected = 12
$deadline = (Get-Date).AddSeconds($TimeoutSec)
$ready = $false
while ((Get-Date) -lt $deadline) {
    $lines = @(docker stack services $Stack --format '{{.Name}}|{{.Replicas}}')
    $ok = 0
    $total = 0
    foreach ($l in $lines) {
        if ($l -match '^(.+)\|(\d+)/(\d+)') {
            $total++
            if ([int]$Matches[2] -ge 1 -and $Matches[2] -eq $Matches[3]) { $ok++ }
        }
    }
    Say ("  Services prets : $ok / $total (attendus : $expected)")
    if ($total -ge $expected -and $ok -eq $total) { $ready = $true; break }
    Start-Sleep -Seconds 10
}

Say ''
docker stack services $Stack
if (-not $ready) {
    Say ''
    Say 'Tous les services ne sont pas prets. Dernieres taches et erreurs :' 'Yellow'
    docker stack ps $Stack --no-trunc --format '{{.Name}} | {{.CurrentState}} | {{.Error}}' | Select-Object -First 30
    Say ''
    Say 'Dernieres lignes de journal des services non prets :' 'Yellow'
    foreach ($l in @(docker stack services $Stack --format '{{.Name}}|{{.Replicas}}')) {
        if ($l -match '^(.+)\|(\d+)/(\d+)' -and $Matches[2] -ne $Matches[3]) {
            $svcName = $Matches[1]
            Say ("--- $svcName") 'Yellow'
            docker service logs $svcName --tail 6 2>&1
        }
    }
}

# ---------------------------------------------------------------
# 4) Tests de fumee
# ---------------------------------------------------------------
Say ''
Say '== 4/4 Tests de fumee ==' 'Cyan'
Add-Result 'Tous les services sont prets' $ready

$r = Get-Retry 'http://localhost/api/'
$okApi = ($null -ne $r -and $r.Content -match '"version"')
Add-Result 'Gateway via Traefik et nginx (http://localhost/api/)' $okApi

$r = Get-Retry 'http://localhost/'
$okFront = ($null -ne $r -and $r.Content -match '<html|<!doctype')
Add-Result 'Frontend via Traefik (http://localhost/)' $okFront

$suffix = Get-Random -Minimum 1000 -Maximum 9999
$body = @{ email = "swarm$suffix@cloudapp.io"; username = "swarm$suffix"; password = (New-Password 14); full_name = 'Test Swarm' } | ConvertTo-Json
$okReg = $false
for ($i = 1; $i -le 10 -and -not $okReg; $i++) {
    try {
        $resp = Invoke-RestMethod -Method Post -Uri 'http://localhost/api/auth/register' -ContentType 'application/json' -Body $body -TimeoutSec 10
        if ($resp.id) { $okReg = $true }
    }
    catch {
        Start-Sleep -Seconds 3
    }
}
Add-Result 'Inscription (Traefik -> nginx -> Gateway -> Auth -> PostgreSQL)' $okReg

# --- Sauvegarde PostgreSQL : creation, controle d'integrite, restauration reelle ---
$bk = $null
for ($i = 1; $i -le 20 -and -not $bk; $i++) {
    $bk = docker ps -q --filter "name=${Stack}_backup" | Select-Object -First 1
    if (-not $bk) { Start-Sleep -Seconds 3 }
}
if (-not $bk) {
    Add-Result 'Service de sauvegarde en marche' $false
}
else {
    $out1 = docker exec $bk bash /usr/local/bin/backup.sh once 2>&1
    Add-Result 'Sauvegarde PostgreSQL creee et controlee (gzip -t)' ($LASTEXITCODE -eq 0)
    $out2 = docker exec $bk bash /usr/local/bin/backup.sh verify 2>&1
    $verifyCode = $LASTEXITCODE
    $verifyText = ($out2 | ForEach-Object { "$_" }) -join "`n"
    Add-Result 'Restauration verifiee dans une base temporaire (lignes par table)' ($verifyCode -eq 0 -and $verifyText -match 'VERIFICATION OK')
    foreach ($line in ($verifyText -split "`n")) {
        if ($line -match '\[backup\]') { Say ('    ' + $line) 'DarkGray' }
    }
}

# --- Notifications automatiques (Gateway -> Notification, e-mail via Resend si configure) :
# la creation d'un projet puis une mise a jour d'avancement doivent produire de nouvelles
# notifications en base (l'envoi d'e-mail lui-meme n'est pas verifiable sans domaine Resend reel). ---
$notifOk = $false
$notifDetail = ''
try {
    $before = (Invoke-RestMethod -Uri 'http://localhost/api/notifications' -TimeoutSec 10).Count
    # Un client reel est necessaire : /projects exige desormais un client_id valide
    # (le Gateway relaie fidelement l'erreur sinon, voir fix-gateway-status.ps1).
    $suffix = Get-Random -Minimum 10000 -Maximum 99999
    $clientBody = "{`"company_name`":`"Test Swarm $suffix`",`"email`":`"test-swarm-$suffix@cloudapp.io`"}"
    $cl = Invoke-RestMethod -Method Post -Uri 'http://localhost/api/clients' -ContentType 'application/json' -Body $clientBody -TimeoutSec 10
    $projBody = "{`"client_id`":$($cl.id),`"name`":`"Test tracage`",`"budget`":1000}"
    $proj = Invoke-RestMethod -Method Post -Uri 'http://localhost/api/projects' -ContentType 'application/json' -Body $projBody -TimeoutSec 10
    if ($proj.id) {
        Invoke-RestMethod -Method Put -Uri "http://localhost/api/projects/$($proj.id)" -ContentType 'application/json' -Body '{"progress":40}' -TimeoutSec 10 | Out-Null
    }
    Start-Sleep -Seconds 2
    $after = (Invoke-RestMethod -Uri 'http://localhost/api/notifications' -TimeoutSec 10).Count
    $notifOk = ($after -gt $before)
    $notifDetail = "client $($cl.id) : $before -> $after notifications"
}
catch { $notifDetail = $_.Exception.Message }
Add-Result 'Notifications automatiques (creation projet + avancement)' $notifOk $notifDetail

# --- Tracage distribue (OpenTelemetry -> Jaeger) : une requete applicative doit produire
# une trace visible dans Jaeger, avec des spans d'au moins 2 services differents. ---
$traceOk = $false
$traceDetail = ''
for ($i = 1; $i -le 15 -and -not $traceOk; $i++) {
    try {
        $svcs = Invoke-RestMethod -Uri 'http://localhost:16686/api/services' -TimeoutSec 5
        $gwTraces = Invoke-RestMethod -Uri 'http://localhost:16686/api/traces?service=gateway&limit=5&lookback=5m' -TimeoutSec 5
        if ($gwTraces.data -and $gwTraces.data.Count -gt 0) {
            $names = @{}
            foreach ($t in $gwTraces.data) {
                foreach ($sp in $t.spans) {
                    $pid_ = $sp.processID
                    $svcName = $t.processes.$pid_.serviceName
                    if ($svcName) { $names[$svcName] = $true }
                }
            }
            if ($names.Keys.Count -ge 2) {
                $traceOk = $true
                $traceDetail = "services relies dans une meme trace : " + (($names.Keys | Sort-Object) -join ', ')
            }
        }
    }
    catch { }
    if (-not $traceOk) { Start-Sleep -Seconds 4 }
}
Add-Result 'Tracage distribue (Jaeger recoit des traces multi-services)' $traceOk $traceDetail
if ($traceOk) { Say '    Interface : http://localhost:16686 (le temps de cette session de test)' 'DarkGray' }

$r = Get-Retry 'http://localhost/grafana/login'
$okGraf = ($null -ne $r -and $r.Content -match 'Grafana')
Add-Result 'Grafana sous /grafana' $okGraf

$upCount = 0
$json = docker run --rm --network traefik-public curlimages/curl -s http://prometheus:9090/api/v1/targets 2>$null
if ($LASTEXITCODE -eq 0 -and $json) {
    try {
        $data = $json | ConvertFrom-Json
        $upCount = @($data.data.activeTargets | Where-Object { $_.health -eq 'up' }).Count
    }
    catch { $upCount = 0 }
}
Add-Result 'Prometheus collecte les services' ($upCount -ge 7) "($upCount cibles UP sur 7 attendues)"

$portDb = docker service inspect "${Stack}_postgres" --format '{{json .Endpoint.Ports}}' 2>$null
Add-Result 'PostgreSQL non publie' ((-not $portDb) -or $portDb -eq 'null' -or $portDb -eq '[]')

# ---------------------------------------------------------------
# Resume
# ---------------------------------------------------------------
$fails = @($results | Where-Object { $_ -like 'FAIL*' }).Count
Say ''
if ($fails -eq 0) {
    Say 'RESULTAT : TOUT EST VERT.' 'Green'
}
else {
    Say ("RESULTAT : $fails test(s) en echec. Copiez la sortie complete de ce script et envoyez-la.") 'Yellow'
}
Say ''
Say 'Application : http://localhost/   |   Grafana : http://localhost/grafana/  (utilisateur admin)'
Say ("Mot de passe Grafana de cette session : $grafanaPassword")
Say 'Etat detaille : docker stack ps cloudprod   |   Journaux : docker service logs cloudprod_auth --tail 30'
Say 'Arret : powershell -ExecutionPolicy Bypass -File scripts\swarm-local-test.ps1 -Down'
}
finally {
    # Ne laisse aucune variable secrete dans la fenetre PowerShell appelante.
    Remove-Item Env:DOCKER_USERNAME, Env:IMAGE_TAG, Env:POSTGRES_PASSWORD, Env:JWT_SECRET_KEY, Env:GRAFANA_ADMIN_PASSWORD, Env:RESEND_API_KEY -ErrorAction SilentlyContinue
}
