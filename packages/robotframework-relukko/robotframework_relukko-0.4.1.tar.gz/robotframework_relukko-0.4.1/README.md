# Robotframework Relukko

See the keywords documentation
https://relukko.gitlab.io/robotframework-relukko/

```robot
*** Settings ***
Library    Relukko    creator=Creator Name


*** Test Cases ***
Test Resource Lock
    Set Up Relukko    http://localhost:3000    some-api-key
    Acquire Relukko    LockName    8m34s
    ${lock}    Keep Relukko Alive For The Next    6m
    Log    ${lock}
    ${lock}    Keep Relukko Alive For The Next "50" Seconds
    Log    ${lock}
    ${lock}    Keep Relukko Alive For The Next 5 Min
    Log    ${lock}
    ${lock}    Add To Current Relukko Expire At Time    7m
    Log    ${lock}
    ${lock}    Add To Current Relukko Expire At Time "60" Seconds
    Log    ${lock}
    ${lock}    Add To Current Relukko Expire At Time 5 Min
    Log    ${lock}
    ${lock}    Update Relukko    creator=Mark
    Log    ${lock}
    ${lock}    Update Relukko    expires_at=2025-01-01T12:34:56.123456Z
    Log    ${lock}
    ${lock}    Get Current Relukko
    Log    ${lock}
    ${expires_at}    Get Relukko Expires At Time
    Log    ${expires_at}
    ${lock}    Get All Relukkos
    Log    ${lock}
    ${lock}    Delete Relukko
    Log    ${lock}
```