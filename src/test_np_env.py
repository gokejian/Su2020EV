#!/usr/bin/env python 
# -*- coding: utf-8 -*-
import vehicle_env
import numpy as np

def main():
    lst = vehicle_env.generate_env_nparray()
    print(len(lst))
    for item in lst:
        print(type(item))
        print("\n==", item, "\n")

if __name__ == "__main__":
    main()