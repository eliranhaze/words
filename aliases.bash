#!/bin/bash

function wadd() {
    python wtool.py --add $1 && git add wlist && git commit -m "added '$1'"
}

function wrem() {
    python wtool.py --remove $1 && git add wlist && git commit -m "removed '$1'"
}

function wrnk() {
    python wtool.py --rank $1
}

function wtrn() {
    python wtool.py --trans "$1" --rank "$1" --exists "$1"
}

function wtrnc() {
    wtrn `getclip`
}

function wgrp() {
    grep $1 wlist
}

function wurl() {
    python count.py --url $1
}

function wurlc() {
    wurl `getclip`
}

function wlinks() {
    python main.py --links $1 --console
}

function wbookmarks() {
    python main.py --bookmarks "$1" --console
}

function wfeed() {
    if [ $2 ]; then
       hours="--hours $2"
    else
       hours=""
    fi
    python main.py --sources "$1" --console $hours
}

alias bd="vi brains/data.py && git add brains/data.py && git add *.pkl && git commit -m 'training data update' && git push"


