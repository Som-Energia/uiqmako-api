import logging

log = logging.getLogger("uiqmako")
log.setLevel(logging.DEBUG) # TODO: From environment

class Formatter(logging.Formatter):
    def format(self, record):
        def color(level):
            if level >= logging.CRITICAL: return '41;30'
            if level >= logging.ERROR: return '31'
            if level >= logging.WARNING: return '33'
            if level >= logging.INFO: return '32'
            return '36;1'
        levelcolor = "\033["+color(record.levelno)+"m"
        levelprefix = levelcolor + record.levelname + "\033[0m:" + " "*(10-len(record.levelname)) 
        formatter = logging.Formatter(
            fmt=(
                "\033[30;1m{asctime}\033[0m "
                + levelprefix + " {message}\033[0m\n"
                "   \033[034m({name} - {pathname}:{lineno})\033[0m"
            ),
            datefmt='%Y-%m-%d %H:%M:%S',
            style='{',
        )
        return formatter.format(record)

handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
handler.setFormatter(Formatter())
log.addHandler(handler)

if False: # Testing
    log.critical("Ejemplo critical")
    log.error("Ejemplo error")
    log.warning("Ejemplo warning")
    log.info("Ejemplo info")
    log.debug("Ejemplo debug")

