# sandlerprops
> A Python interface to the pure-component properties database that originally accompanied the textbook _Chemical, Biochemical, and Engineering Thermodynamics_ (4th edition) by Stan Sandler (Wiley, USA).

## Installation

```sh
pip install sandlerprops
```

## Usage example

```python
>>> from sandlerprops.properties import Properties as P
>>> m=P.get_compound('methane')
>>> m.Molwt
16.043
>>> p.U.Molwt
'g/mol'
>>> m.Tc
190.4
>>> p.U.Tc
'K'
```

## Release History

* 0.0.2
    * Updated dependencies
* 0.0.1
    * Initial version

## Meta

Cameron F. Abrams – cfa22@drexel.edu

Distributed under the MIT license. See ``LICENSE`` for more information.

[https://github.com/cameronabrams](https://github.com/cameronabrams/)

## Contributing

1. Fork it (<https://github.com/cameronabrams/ThermoProblems/fork>)
2. Create your feature branch (`git checkout -b feature/fooBar`)
3. Commit your changes (`git commit -am 'Add some fooBar'`)
4. Push to the branch (`git push origin feature/fooBar`)
5. Create a new Pull Request
