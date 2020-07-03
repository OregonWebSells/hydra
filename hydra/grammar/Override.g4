// Regenerate parser by running 'python setup.py antlr' at project root.
grammar Override;

override: (
      key EQ value?                              // key=value
    | TILDE key (EQ value?)?                     // ~key | ~key=value
    | PLUS key EQ value?                         // +key= | +key=value
) EOF;

key :
    packageOrGroup                               // key
    | packageOrGroup AT package (COLON package)? // group@pkg | group@pkg1:pkg2
    | packageOrGroup AT COLON package            // group@:pkg2
;

value: element | choiceSweep;

choiceSweep: element (COMMA element)+;

package: (ID | DOT_PATH);

packageOrGroup: package | ID (SLASH ID)+;

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
    | BACKSLASH
    | SLASH
    | COLON
    | DASH
    | PLUS
    | DOT
    | ASTERISK
    | DOLLAR
    | DOT_PATH
    | INTERPOLATION
)+;

dictValue: DOPEN (ID COLON element (COMMA ID COLON element)*)? DCLOSE;

listValue: LOPEN (element(COMMA element)*)? LCLOSE;

// Tokens
LOPEN: '[';
LCLOSE: ']';
DOPEN: '{';
DCLOSE: '}';
COMMA: ',';
COLON: ':';
DOLLAR: '$';
EQ: '=';
PLUS: '+';
DASH: '-';
TILDE: '~';
DOT: '.';
BACKSLASH: '\\';
SLASH: '/';
AT: '@';
ASTERISK : '*';

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
DOT_PATH: ID (DOT ID)+;

WS: (' ' | '\t')+ -> channel(HIDDEN);

QUOTED_VALUE: '\'' .*? '\'' | '"' .*? '"' ;

INTERPOLATION:
    DOLLAR DOPEN (
          // interpolation
          (ID | DOT_PATH)
          // custom interpolation
        | ID COLON (ID | QUOTED_VALUE) (COMMA (ID | QUOTED_VALUE))*
    ) DCLOSE;
