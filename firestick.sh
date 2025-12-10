


# list all adb -s 192.168.3.14:5555 shell commands for firestick tv
adb -s 192.168.3.14:5555 shell 192.168.3.14:5555

# list all adb -s 192.168.3.14:5555 shell commands for firestick tv
adb -s 192.168.3.14:5555 shell dumpsys window windows | grep -E 'mCurrentFocus|mFocusedApp'

# list all adb -s 192.168.3.14:5555 shell commands for firestick tv
adb -s 192.168.3.14:5555 shell dumpsys window windows | grep -E 'mCurrentFocus|mFocusedApp' | grep -E 'com.amazon.tv.launcher/com.amazon.tv.launcher.LauncherActivity'

# list all adb -s 192.168.3.14:5555 shell commands for firestick tv
adb -s 192.168.3.14:5555 shell dumpsys window windows | grep -E 'mCurrentFocus|mFocusedApp' | grep -E 'com.amazon.tv.launcher/com.amazon.tv.launcher.LauncherActivity' | grep -E 'com.amazon.tv.launcher/com.amazon.tv.launcher.LauncherActivity'

# list all adb -s 192.168.3.14:5555 shell commands for firestick tv




adb -s 192.168.3.14:5555 shell input keyevent 3
adb -s 192.168.3.14:5555 shell am force-stop com.amazon.firetv.youtube
adb -s 192.168.3.14:5555 shell am start -n com.amazon.firetv.youtube/dev.cobalt.app.MainActivity
adb -s 192.168.3.14:5555 shell input keyevent 19
adb -s 192.168.3.14:5555 shell input keyevent 66
adb -s 192.168.3.14:5555 shell input text alanzoka
adb -s 192.168.3.14:5555 shell input keyevent 66








# Lista de comandos úteis - ADB Fire TV Stick:

# Navegação para cima:

adb -s 192.168.3.14:5555 shell input keyevent 19

# Navegação para baixo:

adb -s 192.168.3.14:5555 shell input keyevent 20

# Navegação para esquerda:

adb -s 192.168.3.14:5555 shell input keyevent 21

# Navegação para a direita:

adb -s 192.168.3.14:5555 shell input keyevent 22

# Tecla Enter:

adb -s 192.168.3.14:5555 shell input keyevent 66

# Tecla Voltar:

adb -s 192.168.3.14:5555 shell input keyevent 4

# Tecla Início:

adb -s 192.168.3.14:5555 shell input keyevent 3

# Tecla Menu*:

adb -s 192.168.3.14:5555 shell input keyevent 1

# Tecla para tocar ou pausar mídia:

adb -s 192.168.3.14:5555 shell input keyevent 85

# Mídia anterior:

adb -s 192.168.3.14:5555 shell input keyevent 88

# Próxima mídia:

adb -s 192.168.3.14:5555 shell input keyevent 87

# Faça uma captura de tela:

adb -s 192.168.3.14:5555 shell screencap -p /sdcard/captura.png

# Desativar animações da interface**:

adb -s 192.168.3.14:5555 shell settings put global animator_duration_scale 0.0

adb -s 192.168.3.14:5555 shell settings put global transition_animation_scale 0.0

adb -s 192.168.3.14:5555 shell settings put global window_animation_scale 0.0


# Listar configurações globais:

adb -s 192.168.3.14:5555 shell settings list global

# Listar todos os pacotes instalados:

adb -s 192.168.3.14:5555 shell pm list packages -f -3

# start package youtube: 
adb -s 192.168.3.14:5555 shell am start -n com.amazon.firetv.youtube/dev.cobalt.app.MainActivity

# start package youtube busca: 
adb -s 192.168.3.14:5555 shell am start -n com.amazon.firetv.youtube/dev.cobalt.app.MainActivity t4375
adb -s 192.168.3.14:5555 shell am start -n com.amazon.firetv.youtube/dev.cobalt.app.SearchActivity

adb -s 192.168.3.14:5555 shell am force-stop com.amazon.firetv.youtube

# send texto to searchSearchActivity

adb -s 192.168.3.14:5555 shell am start -a android.intent.action.SEARCH

# adb -s 192.168.3.14:5555 shell input text "alanzoka"

# start package hbo:
adb -s 192.168.3.14:5555 shell am start -n com.hbo.hbonow/com.hbo.hbonow.activities.SplashActivity


# Listar todos os pacotes:

adb -s 192.168.3.14:5555 shell pm list packages -f

# Desativar um determinado pacote:

adb -s 192.168.3.14:5555 shell pm disable-user --user 0 [Nome_Pacote]

