# lolcode_interpreter

## Code status
- Testcases are now all working in parser (except dun sa mga testcases na may bug talaga).

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
- Case fallthrough is allowed??? Kasi terminated daw ng GTFO yung cases HNGGG BKET KSE INDE AQ NAGBABASA NG SPECS HAHAHAAH
- implement return statements
- Refactor switch case impklementation to allow fallthrough

## Bugs on Testcases
- Visible arguments are separated by `,` instead of `+` (Test Case 5)
- Function parameters are not separated by `YR` and `AN YR` (Test Case 10)
- Case 0 do not have a break statement, if intentional it will fallthrough to the default case (Test Case 8)
- Visible arguments do not have a separator (should be `+`) (Test Case 8)
- Used 'PRODUCKT' instead of 'PRODUKT', resulting into an unidentified keyword error (Test Case 8)
- Visible arguments are separated by `AN` instead of `+` (Test Case 4)