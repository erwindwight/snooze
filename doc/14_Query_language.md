# Query language

Snooze has its own built-in query language to search records and other objects in the database.

# Word search

The basic search will perform a word search.
```
myword
```

# Field search

## Types

The perform a strict equality on a field:
```
host = myhost01
```

It's possible to use strings by quoting them when they contain
special characters. Single quotes and double quotes supported.
Special characters can be escaped with `\` when using quotes.

```
host = "myhost01"
```

> Note: Only expressions composed of alphanumerics, `_`, `-` and `.` are
> supported when omitting quotes.

Integer and floats are also supported:
```
pid = 12345
```
```
x = 3.14
```

Booleans literals `true` and `false` are also supported (case insensitive).

When needed, fields can also be written with string escapes:
```
"my field" = "my value"
```

Arrays and dictionary are represented like in JSON, except the fields of dictionary
that support the unquoted syntax:
```
myarray = [1, 2, 3]
mydict = {mymessage: x, mynumber: 123}
```

Fields support nested queries using `.`:
```
myarray.0 = 1
mydict.mymessage = "x"
```

Field keys with a dot in the name are unsupported (they won't appear in the search), this
is due to the limitation of the backend database (MongoDB).

## Comparison operators

The following operations are supported for fields:
* `=`: Exact match
* `!=`: Not equals
* `~` or `MATCHES`: Regex search
* `?` or `EXISTS`: Field existence (`field?` or `field EXISTS`)
* `>`: Greater than
* `<`: Lower than
* `in`: Check if a value exists in a list (`"myrule" in rules`). The element on the right should be a field name.
Arrays are supported, and it will return if the field contains at least one element (`[1, 2, 3] in myarray` equivalent to `1 in myarray | 2 in myarray | 3 in myarray`)
* `contains`: Same as `in`, with reverse syntax (`rules contains "myrule"`).

Example usage:
```
host = myhost01
process != systemd
message ~ "[Aa]lert"
message MATCHES "[aA]lert"
custom_field?
custom_field EXISTS
x > 10
y < 3.14
"myrule01" in rules
rules contains "myrule01"
[1,2,3] in myarray
myarray contains [1,2,3]
```

# Logic

Basic boolean logic is supported. Note that none of the keyword is case sensitive.
Parenthesis are supported.

## And

The "AND" operation is implicit.
```
host=myhost01 process=systemd
```

Explicit "AND" is also supported like so:
```
host=myhost01 and process=systemd
```

The `&` character is also accepted:
```
host=myhost01 & process=systemd
```

## Or

The "OR" boolean operation is explicit:
```
host=myhost01 or host=myhost02
```


The `|` character is also accepted:
```
host=myhost01 | host=myhost02
```

## Not

The revert the result of a condition, `NOT` can be used.
```
not process=systemd
```

The character `!` is also supported:
```
!process=systemd
```

# Limitations

* The `in` keyword support queries in the backend, but this is not supported bu the query parser (i.e. `type=Postfix in relays`)
* The parser rarely error, thus invalid syntax might still be interpreted without proper feedback.
