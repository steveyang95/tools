#!/bin/bash

function sig() {

echo "SOCAT: Signal $1 received"

case "$1" in
    TERM)
        kill -TERM ${socat_pid}
        ;;
    HUP)
        kill -HUP ${socat_pid}
        ;;
    QUIT)
        kill -QUIT ${socat_pid}
        ;;
    INT)
        kill -INT ${socat_pid}
        ;;
    *)
        echo "SOCAT: Signal :$1: unknown"
        ;;
esac
echo "SOCAT: Signal $1 processed."
}

trap 'echo usr1' SIGUSR1
trap 'sig TERM' SIGTERM
trap 'sig QUIT' SIGQUIT
trap 'sig HUP' SIGHUP
trap 'sig INT' SIGINT



listener=$(netstat -plant | awk '/:50342\s/ {print $7}')
listener_proc=${listener#*/}
listener_pid=${listener%/*}

if [ "$listener_proc" == "msi-extension" ]
then
   echo "SOCAT: No socat process necessary, talking directly to msi-extension"
   # Make supervisord understand we're running OK
   sleep 5
   exit 0
fi

GATEWAY_ADDRESS=""
echo "SOCAT: Deriving gateway address"
while [ -z "$GATEWAY_ADDRESS" ]
do
    GATEWAY_ADDRESS=$(ip route | grep default | cut -d" " -f3)
    if [ -z "$GATEWAY_ADDRESS" ]
    then
        echo "SOCAT: No gateway address. Waiting 3 seconds to try again."
        sleep 3
    fi
done

if [ ! -z "$listener_pid" ]
then
    echo "SOCAT: About to murder unknown listener on my port: $listener"
    kill -KILL ${listener_pid}
fi

echo "SOCAT: Instantiating forwarding to $GATEWAY_ADDRESS"
socat tcp-listen:50342,fork tcp:${GATEWAY_ADDRESS}:50342 &
socat_pid=$!

# need to wait so that traps can interrupt
wait
