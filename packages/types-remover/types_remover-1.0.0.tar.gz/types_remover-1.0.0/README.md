# Types remover(s)

<!-- **My type removers I made taken from [The_Farmer_Was_Replaced](https://github.com/EasternFarmer/The-Farmer-Was-Replaced/) repo and updated as necessary** -->


This packet has two available functions `remove_types_ast` and `remove_types_if`, that are doing almost the same thing
with implementation. <br>

From the tests I can tell you that `remove_types_ast` is on average 3,28 (average from 100 calls) times slower than
`remove_types_if`

### IMPORTANT TO NOTE

- The `remove_types_ast` function removes comments (not doc-strings)
- Both functions turn multi-line data assignation into a one-line statement