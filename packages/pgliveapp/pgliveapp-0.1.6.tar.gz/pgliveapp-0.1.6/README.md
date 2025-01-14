# pgliveApp

This project is a live plotting application using PyQt6 and pglive. It allows you to create real-time plots with customizable settings.

<img src="https://github.com/takumi-nishimura/pgliveApp/blob/master/docs/images/app_image.png" width="600">

## Features

- Real-time data plotting
- Multiple plot support
- Customizable plot titles and layout
- UDP socket communication for data input

## Installation

To install the required dependencies, run:
```sh
pip install pgliveapp
```

or  

```sh
uv add pgliveapp
```

## Usage
To run the application, execute:
```sh
pgliveapp --num <number_of_plots> --cols <number_of_columns> --port <port_number> --ip <ip_address> --xrange <x_range> --yrange <y_range> --x-points <x_points>
```

For example:
```sh
pgliveapp --num 2 --cols 1 --port 4000 --ip localhost --yrange 5 --x-points 500
```

## Arguments
- --num: Number of plots to display (default: 1)
- --cols: Number of columns in the plot layout (default: 1)
- --port: UDP port to listen for incoming data (default: 4000)
- --ip: IP address to bind the UDP socket (default: localhost)
- --xrange: X-axis range (default: None)
- --yrange: Y-axis range (default: None)
- --x-points: Number of points to display on the x-axis (default: 5000)

## License
This project is licensed under the MIT License - see the [LICENSE](LICENCE.txt) file for details.

* **pglive** is licensed under the MIT License - see the [LICENSE](https://github.com/pyqtgraph/pyqtgraph/blob/master/LICENSE.txt)
* **PyQt6** is licensed under the GPL v3 License.
