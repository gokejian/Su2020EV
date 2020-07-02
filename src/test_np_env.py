#!/usr/bin/env python 
# -*- coding: utf-8 -*-
import vehicle_env


def main():
    lst = vehicle_env.generate_env_nparray()
    for item in lst:
        print(type(item))
        print("\n==", item, "\n")

if __name__ == "__main__":
    main()