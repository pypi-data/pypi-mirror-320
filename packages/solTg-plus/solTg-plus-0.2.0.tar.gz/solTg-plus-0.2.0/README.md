# **SolTG+**  
SolTG+ is a test case generator for Solidity smart contracts, building upon the original implementation of [SolTG](https://github.com/BritikovKI/solidity_testgen/tree/main) by Konstantin Britikov.



## **How to Install**  
Before installing SolTG+, ensure all dependencies are installed.

### Instructions to install dependencies on Ubuntu 24.04 

#### **pip and python**

```
sudo apt update
sudo apt install python3.12 python3-pip python3.12-venv
```
---
#### **Foundry**
```
curl -L https://foundry.paradigm.xyz | bash
source ~/.bashrc
foundryup
```
---
#### **solc (0.8.xx)**
```
sudo apt install curl gnupg software-properties-common
sudo add-apt-repository ppa:ethereum/ethereum
sudo apt update
sudo apt install solc
```
---
#### **GenHTML or lcov**
```
sudo apt update
sudo apt install lcov
```
---
#### **Z3 (4.12.1)** 
Building Z3 from source.
cd to an appropriate directory to clone Z3 repo.
```
sudo apt update
sudo apt install build-essential python3 cmake
git clone https://github.com/Z3Prover/z3.git
cd z3
git checkout z3-4.12.1
python scripts/mk_make.py
cd build
make -j$(nproc)
sudo make install
```
---

### **Installation Options**

#### **Option 1**

Once all dependencies have been installed, install the pip package by running (after switching to a virtual environment if necessary):
```
pip install soltg-plus
```
---
#### **Option 2**

Or clone the git repo
```
git clone git@github.com:zuru-zuru/soltgfrontend.git
cd soltgfrontend
``` 
and run (after switching to a virtual environment if necessary):
```
pip install .
```
---
#### **Foundry dependency**
For foundry to generate the coverage report, forge-std must be present inside ```./lib/forge-std``` in the current directory. This can be installed by running:
```
forge install foundry-rs/forge-std --no-commit
```
Note that the above command need not be run if ```./lib/forge-std``` is already present in the current directory (for e.g. its already present in ```soltgfrontend/lib/forge-std``` so SolTG+ can be directly run from the ```soltgfrontend``` directory).

To run SolTG+ use the following command:
```
solTg-plus -i <path to input file/directory> -t <timeout in seconds> 
``` 
---
### **Example directory structure**

```
Current_Directory/
├── input
│   └── Example.sol
└── lib
    └── forge-std
```
running:
```
solTg-plus -i ./input/Example.sol -t 60 
```
will generate the output in ```Current_Directory/test```

---

### **tgnonlin and solc**
Precompiled binaries for modified versions of tgnonlin and solc are included in the deps folder (compiled on Ubuntu 24.04). If they are incompatible with your system, replace them with binaries compiled from the [soltgbackend](https://github.com/zuru-zuru/soltgbackend) repo.



## **Install Docker image**

Alternatively SolTG+ can be installed as a docker image. The only dependency needed to be installed for this is [Docker](https://docs.docker.com/engine/install/)

Also don't forget to get your user permission to interact with docker:
https://stackoverflow.com/questions/48957195/how-to-fix-docker-got-permission-denied-issue

Once docker has been installed, download the image by running:
```
docker pull cs74/soltg-plus:latest
```

And run the following command to use the docker image:
```
docker run  -v <input directory>:/app/input -v <output directory>:/app/test cs74/soltg-plus:latest -i ./input/<path to input file> -t <timeout in seconds>
```
here ```<input directory>``` and ```<output directory>``` are absolute paths to the input and output directory on the host system while ```<path to input file>``` is the relative path from the input directory to the input file on the host system. Make sure that the input file and any other file it imports are inside ```<input directory>``` or its subdirectories so that they are accessible inside the docker container.

e.g. command
```
sudo docker run  -v /home/username/input_dir:/app/input -v /home/username/output_dir:/app/test soltg-plus:latest -i ./input/Example.sol -t 60
```
where path to ```Example.sol``` is ```/home/username/input_dir/Example.sol``` on the host system. All previous contents of the ```output_dir```  will be cleared.



## **Usage Notes**  

1. **Requirements for SolCMC to generate the CHC Encoding**:  
   - Contracts must not be abstract.  
   - There must be least one `assert` statement (e.g., `assert(true);`) in the contract.  
   - SolTG+ will notify if the CHC encoding is not generated.

2. **Input File Compatibility**:  
   - Input files must be compatible with the precompiled `solc` binary in the `deps` folder (`0.8.29`).  
   - If installed via pip or from source, input files must ALSO be compatible with the system's `solc`.  
   - If using Docker, input files must ALSO be compatible with `solc` (`0.8.29`).

---


Example of Contract under Test:
```
contract C {

    uint x;

	function f(uint _x) public {}
	function g(uint _x, uint _y) public {}
	function w(uint _x) public {}


	function i(uint _x) internal {}
}
```
Expected results of Test Generation:
```
import "forge-std/Test.sol";
import "../src/contract_under_test.sol";

contract contract_under_test_Test is Test {
	C c0, c1, c2, ... cN;

	function setUp() public {
		c0 = new C(); c1 = new C(); ... cN = new C();
	}
	function test_0() public {
		c0.f();
		c0.g();
		....
		c0.w();
	}
........
    function test_n() public {
		cN.g();
		cN.w();
		....
		cN.w();
	}
}
```
Example taken from the README.md file of [SolTG's repository](https://github.com/BritikovKI/solidity_testgen/tree/main).







