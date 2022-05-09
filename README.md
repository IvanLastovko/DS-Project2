# DS-Project2

**Authors: Artjom Valdas & Ivan Lastovko**

### Overview
This project was created for the course Distributed Systems (LTAT.06.007) at the University of Tartu. 
In this project we have implemented the The Byzantine General’s problem.
All the generals communicate with each other through Sockets.

### Running
In order to run this project run the `script.sh` script with any integer as an argument (i > 0).
It will open up command prompt where you will need to enter any of the following commands:
* `g-state` - displays all of the created nodes (generals) with indicating their state (faulty / non-faulty) and role (primary / secondary)
* `g-state {general ID} faulty` - changes state of the mentioned node into *faulty*.
* `g-add {K}` - adds *K* amount of generals.
* `g-kill {general ID}` - removes mentioned node from the list of generals.
* `actual-order {attack | retreat}` - primary node will send the order to other generals and it will start the Byzantine General’s problem.

For the algoritm to work properly, the total amount of nodes must be greater or equal to *3k+1* where *k* is the amount of *faulty* generals.
