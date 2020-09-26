# wsl2-forwarding-port-engine

>	Author: Chatdanai Phakaket <br>
>	Email: zchatdanai@gmail.com 

WSL2-forwarding-port-engine is backend of WSL2-forwarding-port cli


## How to install

1. Open WSL2
2. Download the binary with the command 
```
    curl -LO https://github.com/mrzack99s/wsl2-forwarding-port-engine/releases/download/v0.2.0/wfp-engine.exe
    curl -LO https://github.com/mrzack99s/wsl2-forwarding-port-engine/releases/download/v0.2.0/wfp-engine-autorun.vbs
```
3. Make the wfp-engine binary executable.
```
    chmod +x wfp-engine.exe
```
4. Create directory
```
    mkdir /mnt/c/Users/<window-username>/.wfp-engine
```
5. Change window username in wfp-engine-autorun.vbs
6. Move the binary into PATH.
```
    mv ./wfp-engine.exe /mnt/c/Users/MRZacK/.wfp-engine
```
7. Grant permission to administrator to wfp-engine.exe
8. Press key Win+R and paste wfp-engine-autorun.vbs to this below
```
    shell:startup
```

Let's enjoy !!!!


## License

Copyright (c) 2020 - Chatdanai Phakaket

	

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

[http://www.apache.org/licenses/LICENSE-2.0](http://www.apache.org/licenses/LICENSE-2.0)