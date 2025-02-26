#!/bin/bash


source /morello/env/morello-sdk

clang -march=morello --target=aarch64-linux-musl_purecap --sysroot=${MUSL_HOME} mwauth.c -o mwauth_cheri.o -fPIC -static

clang --target=aarch64-linux-gnu --sysroot=/root/musl-aarch64/musl-install mwauth.c -o mwauth_noncheri.o -fPIC  -static
