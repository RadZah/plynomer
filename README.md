# Software system, that solves the problem of getting gas usage read from Gas Meter.


This application uses
- Raspberry Pi Zero for capturing photos, 
- Laravel app to store and serve captured photos,
- Django `application`, that process all photos and extract the gas usage values from them. 
As well it shows the results in form of interactive plots on its homepage. The overview of the results is as following:
  

![Gas meter](media/final_preview.jpg)

1) Last captured image of gasmeter consupmtion value, where the gas consumption value was recognized and considered valid.
2) Interactive plot of processed data - extreme values are removed. Simple Moving Average added. 
3) Interactive plot of all recognised and saved values. Simple Moving Average added.


For each subsystem there is a separate README.md file, that describes details about it.


## Contributing

Contributions are welcome!

## License

This project is licensed under the MIT License.
