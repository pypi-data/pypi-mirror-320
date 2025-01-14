# ADVANCED PROGRAMMING HOMEWORK 3: Extension of the scientific computing Toolbox 

All files and folders for the third assignment of the Advanced Programming course at UniTS, A.2024/45.

## Group Members
- **Giovanni Billo**: billogiova@gmail.com

### Contributions

Python bindings were added for both modules, allowing for seamless use of C++ functions in python.
On the ohter hand, less performance-intensive functions like those generating random vectors to generate a graph of interpolation errors were implemented in oython.

Some functionalities were added and extended:
- Better structure, modularization and code organisation.
- Possibility to build the entire unified ToolBox with setuptools.
- more getter and setter methods for DataFrameWrapper
- python function with C++ callback to reduce the size of the dataframe
- Enhance functor which polimorphically allows classes from both modules to use some magic methods and plot data.

### Performance comparison
The file comparison.py leverages decorators and the functor Compare() to time the speed of our C++ bindings against some popular python libraries like NumPy and SciPy.
As the [DataFrame](https://github.com/hosseinmoein/DataFrame), our implementation lags behind pandas when it also has to format the file the right way. 
However, once a file is in the right format, it performs just as good and sometimes even slightly faster than Pandas.

This is also the case with the InterpolateWrapper module, which is tested against SciPy implementations of the linear, Lahgrange and Cubic splines.

### Testing
All tests available for the C++ module were implemented also for python bindings. 
There is the possibility to enable automated testing frameworks when building the project (see BUILD INSTRUCTIONS below)

## BUILD INSTRUCTIONS
The library can easily be built using setuptools:
Run the following commands in the relevant folder:
```bash
python3 setup.py build_ext
```

One can also enable continuous integration by enabling automated tests via pytest and pytest-watch:
```bash
python3 setup.py build_ext watch_tests
```
This setup will run all of the tests again each time a change is made in any part of the code, ensuring continuous integration and early catching of bugs.

---

```bash
cmake -B build -DCMAKE_BUILD_TYPE=Debug -DINTERPOLATION_MODULE=ON 
cd build
make
```

This compiles a Debug build referring to the default data directory in each of the folders, including the InterpolateWrapper module as a custom visitor. 
Files will contain a `DATA_DIR` variable for referencing the directory in code.

---

