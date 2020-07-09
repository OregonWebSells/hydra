// Regenerate parser by running 'python setup.py antlr' at project root.
grammar Override;

override: (
      key '=' value?                             // key=value
    | '~' key ('=' value?)?                      // ~key | ~key=value
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
fragment DIGIT: [0-9_];
fragment NZ_DIGIT: [1-9];
fragment INT_PART: DIGIT+;
fragment FRACTION: '.' DIGIT+;
fragment POINT_FLOAT: INT_PART? FRACTION | INT_PART '.';
fragment EXPONENT: [eE] [+-]? DIGIT+;
fragment EXPONENT_FLOAT: ( INT_PART | POINT_FLOAT) EXPONENT;
FLOAT: [-]?(POINT_FLOAT | EXPONENT_FLOAT | [Ii][Nn][Ff] | [Nn][Aa][Nn]);
INT: [-]? ('0' | (NZ_DIGIT DIGIT*));

BOOL:
      [Tt][Rr][Uu][Ee]      // TRUE
    | [Ff][Aa][Ll][Ss][Ee]; // FALSE

NULL: [Nn][Uu][Ll][Ll];

fragment CHAR: [a-zA-Z];
ID : (CHAR|'_') (CHAR|DIGIT|'_')*;
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
