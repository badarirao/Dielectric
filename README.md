# Dielectric
 GUI interface for Impedance and Dielectric measurements for the Keysight E4990A impedance analyzer (GPIB). A Chino KP1000C (serial port) with Au-thermocouple is used to control the sample temperature.

## Software appearance
![dielectric_image](https://user-images.githubusercontent.com/47620203/234462607-c9feadbe-a035-437a-86af-11ab859ad78a.jpg)

## Software capabilities

The instrument is controlled in a separate thread so that user interferance does not affect the measurement.

Following features are available
- Frequency sweep at fixed temperature and DC bias
- DC bias sweep at fixed temperature and frequency
- Frequency sweep at varying temperatures: Temperature variation can be continuous, specific interval or set of specific setpoints.
- Data that can be viewed are capacitance & loss, impedance & phase.
- Software also displays the instantaneous impedance and capacitance values at a set frequency and AC voltage which is useful to determine if the prober is in contact with the sample.
- There is also an option to input your email and line token, to get alerts when the measurement has started, finished or when there is a problem with measurement. This is especially useful for long measurements. However, the list of error prompts is not completed yet, and all the errors may not be sent yet.

Feel free to contact me at badari.rao@gmail.com for any help with installation, or code modification to run the program with other models.
 
The following reference from Keysight was used to obtain the commands to control the instrument. https://rfmw.em.keysight.com/wireless/helpfiles/e4990a/index.htm
