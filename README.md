# OctoPrint-EnergenieControl

Uses the Energenie remote control sockets to turn the 3d printer on when OctoPrint connects, and turn it off when it disconnects.
The control board and sockets can be found here: 
https://cpc.farnell.com/energenie/ener002/1-gang-socket-radio-controlled/dp/PL14928
https://cpc.farnell.com/energenie/ener314/rf-controller-board-for-raspberry/dp/SC13489

The plugin doesn’t add any UI to OctoPrint, it just runs when OctoPrint connects to, or disconnects from, the printer. This can be done from the OctoPrint sidebar, but any automatic connections or disconnections will also trigger it.
