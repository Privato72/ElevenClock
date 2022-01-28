# ISTRUZIONI

# Traduci il testo e scrivilo tra "
# ESEMPIO:      originale ->  "This text is in english: value {0}" 
#               traduzione -> "Questo testo è in inglese: valore {0}"
# Se vedi qualcosa come {0}, {1}, mantienilo nella frase tradotta.
# Prestare particolare attenzione a elementi come ":", ecc.

lang_3_1 = {
    "W": "", # The initial of the word week in your language: W for week, S for setmana, etc.
    "Disable the notification badge": "Disattiva il badge di notifica",
    "Override clock default height": "Sovrascrivi l'altezza predefinita dell'orologio",
    "Adjust horizontal clock position": "Regola la posizione orizzontale dell'orologio",
    "Adjust vertical clock position": "Regola la posizione verticale dell'orologio",
    "Export log as a file": "Esporta il diario come file",
    "Copy log to clipboard": "Copia il diario negli appunti",
    "Announcements:": "Annunci",
    "Fetching latest announcement, please wait...": "Recupero dell'ultimo annuncio, attendi prego...",
    "Couldn't load the announcements. Please try again later": "Non è stato possibile caricare gli annunci. Si prega di riprovare più tardi",
    "ElevenClock's log": "Diario di ElevenClock",
    "Pick a color": "Scegli un colore"
}

lang_3 = lang_3_1 | {
    "Hide the clock during 10 seconds when clicked": "Nascondi l'orologio per 10 secondi quando si clicca",
    "Enable low-cpu mode": "Abilita la modalità a bassa-cpu",
    "You might lose functionalities, like the notification counter or the dynamic background": "Potresti perdere delle funzionalità, come il contatore delle notifiche o lo sfondo dinamico",
    "Clock position and size:": "Posizione e dimensioni dell'orologio:",
    "Clock size preferences, position offset, clock at the left, etc.": "Preferenze sulla dimensione dell'orologio, offset di posizione, orologio a sinistra, ecc.",
    "Reset monitor blacklisting status": "Ripristina lo stato di blacklisting del monitor",
    "Reset": "Ripristina",
    "Third party licenses": "Licenze di terze parti",
    "View": "Visualizza",
    "ElevenClock": "ElevenClock",
    "Monitor tools": "Strumenti di monitoraggio",
    "Blacklist this monitor": "Metti in lista nera questo monitor",
    "Third Party Open-Source Software in Elevenclock {0} (And their licenses)": "Software Open-Source di terze parti in Elevenclock {0} (e le loro licenze)",
    "ElevenClock is an Open-Source application made with the help of other libraries made by the community:": "ElevenClock è un'applicazione Open-Source fatta con l'aiuto di altre librerie fatte dalla comunità:",
    "Ok": "Ok",
    "More Info": "Altre Info",
    "About Qt": "Info su Qt",
    "Success": "Successo",
    "The monitors were unblacklisted successfully.": "I monitor sono stati tolti dalla lista nera con successo.",
    "Now you should see the clock everywhere": "Ora dovresti vedere l'orologio dappertutto",
    "Ok": "Ok",
    "Blacklist Monitor": "Monitoraggio della lista nera",
    "Blacklisting a monitor will hide the clock on this monitor permanently.": "La lista nera di un monitor nasconderà l'orologio su questo monitor in modo permanente.",
    "This action can be reverted from the settings window. under <b>Clock position and size</b>": "Questa azione può essere annullata dalla finestra delle impostazioni. in <b>posizione e dimensione dell'orologio</b>",
    "Are you sure do you want to blacklist the monitor \"{0}\"?": "Sei sicuro di voler mettere in lista nera il monitor \"{0}\"?",
    "Yes": "Si",
    "No": "No",
}

lang_2_9_2 = lang_3 | {
    "Reload log": "Ricarica diario",
    "Do not show the clock on secondary monitors": "Non mostrare l'orologio sui monitor secondari",
    "Disable clock taskbar background color (make clock transparent)": "Disattiva il colore di sfondo della barra delle applicazioni dell'orologio (rende l'orologio trasparente)",
    "Open the welcome wizard": "Apri la procedura guidata di benvenuto",
    " (ALPHA STAGE, MAY NOT WORK)": " (FASE ALFA, POTREBBE NON FUNZIONARE)",
    "Welcome to ElevenClock": "Benvenuti su ElevenClock",
    "Skip": "Salta",
    "Start": "Avvia",
    "Next": "Avanti",
    "Finish": "Finito",
}

lang_2_9 = lang_2_9_2 | {
    "Task Manager": "Gestione attività",
    "Change date and time": "Cambia data e ora",
    "Notification settings": "Impostazioni di notifica",
    "Updates, icon tray, language": "Aggiornamenti, barra delle icone, lingua",
    "Hide extended options from the clock right-click menu (needs a restart to be aplied)": "Nascondi le opzioni estese dal menu dell'orologio con il tasto destro del mouse (ha bisogno di un riavvio per essere applicato)",
    "Fullscreen behaviour, clock position, 1st monitor clock, other miscellanious settings": "Comportamento a schermo intero, posizione dell'orologio, orologio del primo monitor, altre impostazioni varie",
    'Add the "Show Desktop" button on the left corner of every clock': 'Aggiungi il pulsante "Mostra Desktop" sull'angolo sinistro di ogni orologio',
    'You might need to set a custom background color for this to work.&nbsp;More info <a href="{0}" style="color:DodgerBlue">HERE</a>': 'Potrebbe essere necessario impostare un colore di sfondo personalizzato perché questo funzioni.&nbsp;Maggiori informazioni <a href="{0}" style="color:DodgerBlue">Qui</a>',
    "Clock's font, font size, font color and background, text alignment": "Carattere dell'orologio, dimensione del carattere, colore del carattere e sfondo, allineamento del testo",
    "Date format, Time format, seconds,weekday, weeknumber, regional settings": "Formato della data, formato dell'ora, secondi, giorno della settimana, numero della settimana, impostazioni regionali",
    "Testing features and error-fixing tools": "Funzionalità di test e strumenti per la correzione degli errori",
    "Language pack author(s), help translating ElevenClock": "Autore/i del pacchetto linguistico, aiuto alla traduzione di ElevenClock",
    "Info, report a bug, submit a feature request, donate, about": "Info, segnala un bug, invia una richiesta di funzionalità, donare, Info su",
    "Log, debugging information": "Diario, informazioni di debug",
}

lang_2_8 = lang_2_9 | {
    "Force the clock to be at the top of the screen": "Forza l'orologio ad essere nella parte superiore dello schermo",
    "Show the clock on the primary screen": "Mostra l'orologio sullo schermo principale",
    "Use a custom font color": "Usa un colore personalizzato per il carattere",
    "Use a custom background color": "Usa un colore personalizzato per lo sfondo",
    "Align the clock text to the center": "Allinea il testo dell'orologio al centro",
    "Select custom color": "Seleziona un colore personalizzato",
    "Hide the clock when a program occupies all screens": "Nascondi l'orologio quando un programma occupa tutte le schermate",
}

lang2_7_bis = lang_2_8 | {
    "Use a custom font": "Usa un carattere personalizzato",
    "Use a custom font size": "Usa una dimensione del caattere personalizzata",
    "Enable hide when multi-monitor fullscreen apps are running": "Abilita l'occultamento quando sono in esecuzione app a schermo intero su più monitor",
    "<b>{0}</b> needs to be enabled to change this setting": "<b>{0}</b> deve essere abilitato per cambiare questa impostazione",
    "<b>{0}</b> needs to be disabled to change this setting": "<b>{0}</b> deve essere disabilitato per cambiare questa impostazione",
}

lang2_7 = lang2_7_bis | {
    " (This feature has been disabled because it should work by default. If it is not, please report a bug)": "(Questa funzionalità è stata disabilitata perchè dovrebbe funzionare di default. Se non funziona, segnala un bug)",
    "ElevenClock's language": "Lingua di ElevenClock"
}

lang2_6 = lang2_7 | {
    "About Qt6 (PySide6)": "Info su Qt6 (PySide6)",
    "About": "Info su",
    "Alternative non-SSL update server (This might help with SSL errors)": "Server di aggiornamento alternativo non-SSL (Questo potrebbe aiutare con gli errori SSL)",
    "Fixes and other experimental features: (Use ONLY if something is not working)": "Correzioni e altre funzionalità sperimentali: (Usale SOLO se qualcosa non funziona)",
    "Show week number on the clock": "Mostra il numero della settimana",
}

lang2_5 = lang2_6 | {
    "Hide the clock when RDP Client or Citrix Workspace are running": "Nascondi l'orologio quando RDP Client o Citrix Workspace sono in esecuzione",
    "Clock Appearance:": "Aspetto dell'orlogio",
    "Force the clock to have black text": "Forza l'orologio ad avere il testo scuro",
    " - It is required that the Dark Text checkbox is disabled": "- È necessario che la casella di controllo Dark Text sia disabilitata",
    "Debbugging information:": "Informazioni di debug",
    "Open ElevenClock's log": "Apri i log di ElevenClock",
}

lang2_4 = lang2_5 | {
    # Added text in version 2.4
    "Show the clock on the primary screen (Useful if clock is set on the left)": "Mostra l'orologio sullo schermo principale (Utile se l'orologio è impostato a sinistra)",
    "Show weekday on the clock"  :"Visualizza il giorno della settimana",
}

lang2_3 = lang2_4 | {
    #Context menu
    "ElevenClock Settings"      :"Impostazioni ElevenClock", # Also settings title
    "Reload Clocks"             :"Ricarica",
    "ElevenClock v{0}"          :"ElevenClock v{0}",
    "Restart ElevenClock"       :"Riavvia ElevenClock",
    "Hide ElevenClock"          :"Nascondi ElevenClock",
    "Quit ElevenClock"          :"Esci",
    
    #General settings section
    "General Settings:"                                                                 :"Impostazioni generali:",
    "Automatically check for updates"                                                   :"Rileva automaticamente gli aggiornamenti",
    "Automatically install available updates"                                           :"Installa automaticamente gli aggiornamenti",
    "Enable really silent updates"                                                      :"Abilita aggiornamenti silenziosi",
    "Bypass update provider authenticity check (NOT RECOMMENDED, AT YOUR OWN RISK)"     :"Ignora il controllo di autenticità del provider di aggiornamento (NON RACCOMANDATO, A TUO RISCHIO)",
    "Show ElevenClock on system tray"                                                   :"Visualizza ElevenClock sulla barra di sistema",
    "Alternative clock alignment (may not work)"                                        :"Allineamento alternativo dell'orologio (potrebbe non funzionare)",
    "Change startup behaviour"                                                          :"Cambia il comportamento in avvio",
    "Change"                                                                            :"Cambia",
    "<b>Update to the latest version!</b>"                                             :"<b>Aggiorna all'ultima versione!</b>",
    "Install update"                                                                    :"Installa l'aggiornamento",
    
    #Clock settings
    "Clock Settings:"                                              :"Impostazioni orologio:",
    "Hide the clock in fullscreen mode"                            :"Nascondi l'orologio in modalità a schermo intero",
    "Hide the clock when RDP client is active"                     :"Nascondi l'orologio quando il client RDP è attivo",
    "Force the clock to be at the bottom of the screen"            :"Forza l'orologio ad essere al fondo dello schermo",
    "Show the clock when the taskbar is set to hide automatically" :"Visualizza l'orologio quando la barra delle applicazioni è impostata a Nascondi",
    "Fix the hyphen/dash showing over the month"                   :"Corregge la visualizzazione del trattino sul mese",
    "Force the clock to have white text"                           :"Forza l'orologio ad usare testo bianco",
    "Show the clock at the left of the screen"                     :"Visualizza l'orologio alla sinistra dello schermo",
    
    #Date & time settings
    "Date & Time Settings:"                             :"Impostazioni data e Ora:",
    "Show seconds on the clock"                         :"Visualizza i secondi",
    "Show date on the clock"                            :"Visualizza la data",
    "Show time on the clock"                            :"Visualizza l'ora",
    "Change date and time format (Regional settings)"   :"Cambia il formato di visualizzazione della data e dell'ora (Impostazioni regionali)",
    "Regional settings"                                 :"Impostazioni regionali",
    
    #About the language pack
    "About the language pack:"                  :"Informazioni sulla traduzione",
    "Translated to English by martinet101"      :"Tradotto in Italiano da Parapongo, zuidstroopwafel", # Here, make sute to give you some credits:  Translated to LANGUAGE by USER/NAME/PSEUDONYM/etc. 
    "Translate ElevenClock to your language"    :"Traduci ElevenClock nella tua lingua",
    "Get started"                               :"Inizia",
    
    #About ElevenClock
    "About ElevenClock version {0}:"            :"Informazioni sulla versione {0} di ElevenClock",
    "View ElevenClock's homepage"               :"Visualizza l'homepage di ElevenClock",
    "Open"                                      :"Apri",
    "Report an issue/request a feature"         :"Segnala un problema/richiedi una nuova funzionalità",
    "Report"                                    :"Segnala",
    "Support the dev: Give me a coffee☕"       :"Supporta lo sviluppatore: donami un caffè☕",
    "Open page"                                 :"Apri la pagina",
    "Icons by Icons8"                           :"Icone tratte da Icons8", # Here, the word "Icons8" should not be translated
    "Webpage"                                   :"Pagina Web",
    "Close settings"                            :"Chiudi le impostazioni",
    "Close"                                     :"Chiudi",
}

lang = lang2_3
