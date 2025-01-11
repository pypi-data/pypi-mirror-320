#! /usr/bin/env bash

function abcli_install_blue_sandbox() {
    abcli_git_clone https://github.com/microsoft/building-damage-assessment.git
}

abcli_install_module blue_sandbox 1.1.1
