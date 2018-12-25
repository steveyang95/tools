#!/bin/bash

function sig() {

echo "Signal $1 received"

case "$1" in
    TERM)
        nginx -s stop || exit 255
        ;;
    HUP)
        nginx -s reload || exit 255
        ;;
    QUIT)
        nginx -s quit || exit 255
        ;;
    INT)
        echo "$0 received SIGINT.  Stopping nginx."
        nginx -s stop || exit 255
        ;;
    *)
        echo "Signal :$1: unknown"
        ;;
esac
}

trap 'echo usr1' SIGUSR1
trap 'sig TERM' SIGTERM
trap 'sig QUIT' SIGQUIT
trap 'sig HUP' SIGHUP
trap 'sig INT' SIGINT

# quietly kill any nginx running if for some reason we've restarted
nginx -s stop >/dev/null 2>&1 || true

UWSGI_STARTED=false
echo "$0 waiting for UWSGI"

while ! $UWSGI_STARTED
do
    COUNT=$(pgrep uwsgi | wc -l)
    if [ $COUNT -gt 2 ]; then
        UWSGI_STARTED=true
    else
        UWSGI_STARTED=false
    fi
    sleep 0.5
done

echo "$0 uwsgi running, launching nginx"

nginx -g "daemon off;" &

# need to wait so that traps can interrupt
wait

exit 0
