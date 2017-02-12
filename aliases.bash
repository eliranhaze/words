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
    python wtool.py --trans $1 --rank $1 --exists $1
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

function wlinks() {
    python main.py --links $1
}

function wurlc() {
    wurl `getclip`
}

alias bd="vi brains/data.py && git add brains/data.py && git commit -m 'training data update' && git push"


