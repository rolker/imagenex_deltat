#!/usr/bin/env python3

from imagenex_deltat.sonar import DeltaT

sonar = DeltaT()

data = sonar.ping()
for d in data:
    print(d)
    print(d.echo_data)

