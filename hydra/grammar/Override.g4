// Regenerate parser by running 'python setup.py antlr' at project root.
grammar Override;

override: (
      key '=' value?                              // key=value
    | '~' key ('=' value?)?                     // ~key | ~key=value
    | '+' key '=' value?                         // +key= | +key=value
) EOF;

key :
    packageOrGroup                              // key
    | packageOrGroup '@' package (':' package)? // group@pkg | group@pkg1:pkg2
    | packageOrGroup '@:' package               // group@:pkg2
;

value: element | choiceSweep;

choiceSweep:
      element (',' element)+
    | 'choice' listValue;

package: (ID | DOT_PATH);

packageOrGroup: package | ID ('/' ID)+;

element:
      NULL
    | QUOTED_VALUE
    | primitive
    | listValue
    | dictValue
;

primitive: (
      ID
    | INT
    | FLOAT
    | BOOL
    | DOT_PATH
    | INTERPOLATION
    | '\\'
    | '/'
    | ':'
    | '-'
    | '+'
    | '.'
    | '$'
)+;

dictValue: '{' (ID ':' element (',' ID ':' element)*)? '}';

listValue: '[' (element(',' element)*)? ']';

// Types
INT: [+-]?('0' | [1-9][0-9_]*);
// does not currently support scientific notation. can be added later
fragment NAN: [Nn][Aa][Nn];
fragment INF: [Ii][Nn][Ff];
FLOAT: ([+-]?([0-9_]+ '.' [0-9_]+ | INF)|NAN);

fragment TRUE: [Tt][Rr][Uu][Ee];
fragment FALSE: [Ff][Aa][Ll][Ss][Ee];
BOOL: TRUE|FALSE;

NULL: [Nn][Uu][Ll][Ll];

ID : [a-zA-Z0-9_]+;
DOT_PATH: ID ('.' ID)+;

WS: (' ' | '\t')+ -> channel(HIDDEN);

QUOTED_VALUE: '\'' .*? '\'' | '"' .*? '"' ;

INTERPOLATION:
    '${' (
          // interpolation
          (ID | DOT_PATH)
          // custom interpolation
        | ID ':' (ID | QUOTED_VALUE) (',' (ID | QUOTED_VALUE))*
    ) '}';
