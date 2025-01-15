#!/bin/bash
wasm-pack build --release . -- -Z build-std=std,panic_abort -Z build-std-features=panic_immediate_abort --features wasm
