# lolcode_interpreter

## Test Cases Working

- [x] 1_variables
- [x] 2_gimmeh
- [x] 3_arith
- [ ] 4_smoosh_assign
- [ ] 5_bool
- [ ] 6_comparison
- [ ] 7_ifelse
- [ ] 8_switch
- [ ] 9_loops
- [ ] 10_functions

## Todo
- Clean up debug print statements
- Different flow control statements can be nested which could be a pain in the ass during semantic analyzer. It is a bonus though.
- Check every usage of `self.is_literal` in parser, there must be a string delimiter case catcher everytime the said function is called.
- Decide whether the loop identifier will share the same namespace as variable identifiers
- Gawing darkmode yung terminal HAHAHAHA