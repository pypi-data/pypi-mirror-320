#include "tree_sitter/parser.h"

#if defined(__GNUC__) || defined(__clang__)
#pragma GCC diagnostic ignored "-Wmissing-field-initializers"
#endif

#define LANGUAGE_VERSION 14
#define STATE_COUNT 79
#define LARGE_STATE_COUNT 11
#define SYMBOL_COUNT 43
#define ALIAS_COUNT 0
#define TOKEN_COUNT 23
#define EXTERNAL_TOKEN_COUNT 0
#define FIELD_COUNT 0
#define MAX_ALIAS_SEQUENCE_LENGTH 6
#define PRODUCTION_ID_COUNT 1

enum ts_symbol_identifiers {
  anon_sym_COLON = 1,
  anon_sym_COLON_EQ = 2,
  anon_sym_LPAREN = 3,
  anon_sym_RPAREN = 4,
  anon_sym_EQ_GT = 5,
  anon_sym_DASH_GT = 6,
  anon_sym_Sort = 7,
  anon_sym_POUND = 8,
  aux_sym_bound_var_token1 = 9,
  anon_sym_PLUS = 10,
  anon_sym_1 = 11,
  anon_sym_Max = 12,
  anon_sym_COMMA = 13,
  anon_sym_IMax = 14,
  sym_identifier = 15,
  sym_def_key = 16,
  sym_thm_key = 17,
  sym_ps_key = 18,
  anon_sym_DASH_DASH = 19,
  aux_sym_comment_token1 = 20,
  anon_sym_SLASH_DASH = 21,
  aux_sym_comment_token2 = 22,
  sym_start = 23,
  sym_command = 24,
  sym_definition = 25,
  sym_theorem = 26,
  sym_proofstep = 27,
  sym_action = 28,
  sym_search = 29,
  sym_expr = 30,
  sym_primary = 31,
  sym_app = 32,
  sym_lambda = 33,
  sym_lambda_arg = 34,
  sym_forall = 35,
  sym_forall_arg = 36,
  sym_sort = 37,
  sym_const = 38,
  sym_bound_var = 39,
  sym_level = 40,
  sym_comment = 41,
  aux_sym_start_repeat1 = 42,
};

static const char * const ts_symbol_names[] = {
  [ts_builtin_sym_end] = "end",
  [anon_sym_COLON] = ":",
  [anon_sym_COLON_EQ] = ":=",
  [anon_sym_LPAREN] = "(",
  [anon_sym_RPAREN] = ")",
  [anon_sym_EQ_GT] = "=>",
  [anon_sym_DASH_GT] = "->",
  [anon_sym_Sort] = "Sort",
  [anon_sym_POUND] = "#",
  [aux_sym_bound_var_token1] = "bound_var_token1",
  [anon_sym_PLUS] = "+",
  [anon_sym_1] = "1",
  [anon_sym_Max] = "Max",
  [anon_sym_COMMA] = ",",
  [anon_sym_IMax] = "IMax",
  [sym_identifier] = "identifier",
  [sym_def_key] = "def_key",
  [sym_thm_key] = "thm_key",
  [sym_ps_key] = "ps_key",
  [anon_sym_DASH_DASH] = "--",
  [aux_sym_comment_token1] = "comment_token1",
  [anon_sym_SLASH_DASH] = "/-",
  [aux_sym_comment_token2] = "comment_token2",
  [sym_start] = "start",
  [sym_command] = "command",
  [sym_definition] = "definition",
  [sym_theorem] = "theorem",
  [sym_proofstep] = "proofstep",
  [sym_action] = "action",
  [sym_search] = "search",
  [sym_expr] = "expr",
  [sym_primary] = "primary",
  [sym_app] = "app",
  [sym_lambda] = "lambda",
  [sym_lambda_arg] = "lambda_arg",
  [sym_forall] = "forall",
  [sym_forall_arg] = "forall_arg",
  [sym_sort] = "sort",
  [sym_const] = "const",
  [sym_bound_var] = "bound_var",
  [sym_level] = "level",
  [sym_comment] = "comment",
  [aux_sym_start_repeat1] = "start_repeat1",
};

static const TSSymbol ts_symbol_map[] = {
  [ts_builtin_sym_end] = ts_builtin_sym_end,
  [anon_sym_COLON] = anon_sym_COLON,
  [anon_sym_COLON_EQ] = anon_sym_COLON_EQ,
  [anon_sym_LPAREN] = anon_sym_LPAREN,
  [anon_sym_RPAREN] = anon_sym_RPAREN,
  [anon_sym_EQ_GT] = anon_sym_EQ_GT,
  [anon_sym_DASH_GT] = anon_sym_DASH_GT,
  [anon_sym_Sort] = anon_sym_Sort,
  [anon_sym_POUND] = anon_sym_POUND,
  [aux_sym_bound_var_token1] = aux_sym_bound_var_token1,
  [anon_sym_PLUS] = anon_sym_PLUS,
  [anon_sym_1] = anon_sym_1,
  [anon_sym_Max] = anon_sym_Max,
  [anon_sym_COMMA] = anon_sym_COMMA,
  [anon_sym_IMax] = anon_sym_IMax,
  [sym_identifier] = sym_identifier,
  [sym_def_key] = sym_def_key,
  [sym_thm_key] = sym_thm_key,
  [sym_ps_key] = sym_ps_key,
  [anon_sym_DASH_DASH] = anon_sym_DASH_DASH,
  [aux_sym_comment_token1] = aux_sym_comment_token1,
  [anon_sym_SLASH_DASH] = anon_sym_SLASH_DASH,
  [aux_sym_comment_token2] = aux_sym_comment_token2,
  [sym_start] = sym_start,
  [sym_command] = sym_command,
  [sym_definition] = sym_definition,
  [sym_theorem] = sym_theorem,
  [sym_proofstep] = sym_proofstep,
  [sym_action] = sym_action,
  [sym_search] = sym_search,
  [sym_expr] = sym_expr,
  [sym_primary] = sym_primary,
  [sym_app] = sym_app,
  [sym_lambda] = sym_lambda,
  [sym_lambda_arg] = sym_lambda_arg,
  [sym_forall] = sym_forall,
  [sym_forall_arg] = sym_forall_arg,
  [sym_sort] = sym_sort,
  [sym_const] = sym_const,
  [sym_bound_var] = sym_bound_var,
  [sym_level] = sym_level,
  [sym_comment] = sym_comment,
  [aux_sym_start_repeat1] = aux_sym_start_repeat1,
};

static const TSSymbolMetadata ts_symbol_metadata[] = {
  [ts_builtin_sym_end] = {
    .visible = false,
    .named = true,
  },
  [anon_sym_COLON] = {
    .visible = true,
    .named = false,
  },
  [anon_sym_COLON_EQ] = {
    .visible = true,
    .named = false,
  },
  [anon_sym_LPAREN] = {
    .visible = true,
    .named = false,
  },
  [anon_sym_RPAREN] = {
    .visible = true,
    .named = false,
  },
  [anon_sym_EQ_GT] = {
    .visible = true,
    .named = false,
  },
  [anon_sym_DASH_GT] = {
    .visible = true,
    .named = false,
  },
  [anon_sym_Sort] = {
    .visible = true,
    .named = false,
  },
  [anon_sym_POUND] = {
    .visible = true,
    .named = false,
  },
  [aux_sym_bound_var_token1] = {
    .visible = false,
    .named = false,
  },
  [anon_sym_PLUS] = {
    .visible = true,
    .named = false,
  },
  [anon_sym_1] = {
    .visible = true,
    .named = false,
  },
  [anon_sym_Max] = {
    .visible = true,
    .named = false,
  },
  [anon_sym_COMMA] = {
    .visible = true,
    .named = false,
  },
  [anon_sym_IMax] = {
    .visible = true,
    .named = false,
  },
  [sym_identifier] = {
    .visible = true,
    .named = true,
  },
  [sym_def_key] = {
    .visible = true,
    .named = true,
  },
  [sym_thm_key] = {
    .visible = true,
    .named = true,
  },
  [sym_ps_key] = {
    .visible = true,
    .named = true,
  },
  [anon_sym_DASH_DASH] = {
    .visible = true,
    .named = false,
  },
  [aux_sym_comment_token1] = {
    .visible = false,
    .named = false,
  },
  [anon_sym_SLASH_DASH] = {
    .visible = true,
    .named = false,
  },
  [aux_sym_comment_token2] = {
    .visible = false,
    .named = false,
  },
  [sym_start] = {
    .visible = true,
    .named = true,
  },
  [sym_command] = {
    .visible = true,
    .named = true,
  },
  [sym_definition] = {
    .visible = true,
    .named = true,
  },
  [sym_theorem] = {
    .visible = true,
    .named = true,
  },
  [sym_proofstep] = {
    .visible = true,
    .named = true,
  },
  [sym_action] = {
    .visible = true,
    .named = true,
  },
  [sym_search] = {
    .visible = true,
    .named = true,
  },
  [sym_expr] = {
    .visible = true,
    .named = true,
  },
  [sym_primary] = {
    .visible = true,
    .named = true,
  },
  [sym_app] = {
    .visible = true,
    .named = true,
  },
  [sym_lambda] = {
    .visible = true,
    .named = true,
  },
  [sym_lambda_arg] = {
    .visible = true,
    .named = true,
  },
  [sym_forall] = {
    .visible = true,
    .named = true,
  },
  [sym_forall_arg] = {
    .visible = true,
    .named = true,
  },
  [sym_sort] = {
    .visible = true,
    .named = true,
  },
  [sym_const] = {
    .visible = true,
    .named = true,
  },
  [sym_bound_var] = {
    .visible = true,
    .named = true,
  },
  [sym_level] = {
    .visible = true,
    .named = true,
  },
  [sym_comment] = {
    .visible = true,
    .named = true,
  },
  [aux_sym_start_repeat1] = {
    .visible = false,
    .named = false,
  },
};

static const TSSymbol ts_alias_sequences[PRODUCTION_ID_COUNT][MAX_ALIAS_SEQUENCE_LENGTH] = {
  [0] = {0},
};

static const uint16_t ts_non_terminal_alias_map[] = {
  0,
};

static const TSStateId ts_primary_state_ids[STATE_COUNT] = {
  [0] = 0,
  [1] = 1,
  [2] = 2,
  [3] = 3,
  [4] = 4,
  [5] = 5,
  [6] = 6,
  [7] = 7,
  [8] = 8,
  [9] = 9,
  [10] = 10,
  [11] = 11,
  [12] = 12,
  [13] = 13,
  [14] = 12,
  [15] = 2,
  [16] = 3,
  [17] = 4,
  [18] = 18,
  [19] = 19,
  [20] = 20,
  [21] = 21,
  [22] = 22,
  [23] = 23,
  [24] = 24,
  [25] = 25,
  [26] = 18,
  [27] = 27,
  [28] = 24,
  [29] = 25,
  [30] = 30,
  [31] = 31,
  [32] = 32,
  [33] = 33,
  [34] = 34,
  [35] = 35,
  [36] = 36,
  [37] = 37,
  [38] = 32,
  [39] = 39,
  [40] = 34,
  [41] = 37,
  [42] = 36,
  [43] = 33,
  [44] = 35,
  [45] = 45,
  [46] = 46,
  [47] = 47,
  [48] = 48,
  [49] = 49,
  [50] = 46,
  [51] = 51,
  [52] = 52,
  [53] = 53,
  [54] = 54,
  [55] = 55,
  [56] = 56,
  [57] = 57,
  [58] = 58,
  [59] = 59,
  [60] = 57,
  [61] = 61,
  [62] = 62,
  [63] = 63,
  [64] = 64,
  [65] = 65,
  [66] = 66,
  [67] = 67,
  [68] = 68,
  [69] = 69,
  [70] = 70,
  [71] = 71,
  [72] = 72,
  [73] = 71,
  [74] = 70,
  [75] = 72,
  [76] = 76,
  [77] = 68,
  [78] = 78,
};

static bool ts_lex(TSLexer *lexer, TSStateId state) {
  START_LEXER();
  eof = lexer->eof(lexer);
  switch (state) {
    case 0:
      if (eof) ADVANCE(18);
      ADVANCE_MAP(
        '#', 27,
        '(', 22,
        ')', 23,
        '+', 30,
        ',', 34,
        '-', 3,
        '/', 4,
        '1', 32,
        ':', 20,
        '=', 15,
        'I', 36,
        'M', 37,
        'S', 43,
        'd', 39,
        'p', 45,
        't', 41,
      );
      if (('\t' <= lookahead && lookahead <= '\r') ||
          lookahead == ' ') SKIP(0);
      if (('0' <= lookahead && lookahead <= '9')) ADVANCE(28);
      if (lookahead == '\'' ||
          lookahead == '.' ||
          ('A' <= lookahead && lookahead <= 'Z') ||
          lookahead == '_' ||
          ('a' <= lookahead && lookahead <= 'z')) ADVANCE(49);
      END_STATE();
    case 1:
      ADVANCE_MAP(
        '#', 27,
        '(', 22,
        ')', 23,
        '-', 3,
        '/', 4,
        ':', 19,
        '=', 15,
        'S', 43,
      );
      if (('\t' <= lookahead && lookahead <= '\r') ||
          lookahead == ' ') SKIP(1);
      if (lookahead == '\'' ||
          ('.' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z') ||
          lookahead == '_' ||
          ('a' <= lookahead && lookahead <= 'z')) ADVANCE(49);
      END_STATE();
    case 2:
      if (lookahead == '-') ADVANCE(53);
      END_STATE();
    case 3:
      if (lookahead == '-') ADVANCE(53);
      if (lookahead == '>') ADVANCE(25);
      END_STATE();
    case 4:
      if (lookahead == '-') ADVANCE(60);
      END_STATE();
    case 5:
      if (lookahead == '-') ADVANCE(6);
      if (lookahead == '/') ADVANCE(7);
      if (('\t' <= lookahead && lookahead <= '\r') ||
          lookahead == ' ') ADVANCE(5);
      if (lookahead != 0) ADVANCE(8);
      END_STATE();
    case 6:
      if (lookahead == '-') ADVANCE(54);
      if (lookahead == '/') ADVANCE(63);
      if (lookahead != 0) ADVANCE(8);
      END_STATE();
    case 7:
      if (lookahead == '-') ADVANCE(61);
      if (lookahead != 0) ADVANCE(8);
      END_STATE();
    case 8:
      if (lookahead == '-') ADVANCE(13);
      if (lookahead != 0) ADVANCE(8);
      END_STATE();
    case 9:
      if (lookahead == '-') ADVANCE(2);
      if (lookahead == '/') ADVANCE(4);
      if (lookahead == '1') ADVANCE(31);
      if (('\t' <= lookahead && lookahead <= '\r') ||
          lookahead == ' ') SKIP(9);
      END_STATE();
    case 10:
      if (lookahead == '-') ADVANCE(2);
      if (lookahead == '/') ADVANCE(4);
      if (lookahead == 'I') ADVANCE(36);
      if (lookahead == 'M') ADVANCE(37);
      if (('\t' <= lookahead && lookahead <= '\r') ||
          lookahead == ' ') SKIP(10);
      if (('0' <= lookahead && lookahead <= '9')) ADVANCE(28);
      if (lookahead == '\'' ||
          lookahead == '.' ||
          ('A' <= lookahead && lookahead <= 'Z') ||
          lookahead == '_' ||
          ('a' <= lookahead && lookahead <= 'z')) ADVANCE(49);
      END_STATE();
    case 11:
      if (lookahead == '-') ADVANCE(2);
      if (lookahead == '/') ADVANCE(4);
      if (('\t' <= lookahead && lookahead <= '\r') ||
          lookahead == ' ') SKIP(11);
      if (lookahead == '\'' ||
          ('.' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z') ||
          lookahead == '_' ||
          ('a' <= lookahead && lookahead <= 'z')) ADVANCE(49);
      END_STATE();
    case 12:
      if (lookahead == '-') ADVANCE(2);
      if (lookahead == '/') ADVANCE(4);
      if (('\t' <= lookahead && lookahead <= '\r') ||
          lookahead == ' ') SKIP(12);
      if (('0' <= lookahead && lookahead <= '9')) ADVANCE(29);
      END_STATE();
    case 13:
      if (lookahead == '/') ADVANCE(63);
      if (lookahead != 0) ADVANCE(8);
      END_STATE();
    case 14:
      if (lookahead == '=') ADVANCE(21);
      END_STATE();
    case 15:
      if (lookahead == '>') ADVANCE(24);
      END_STATE();
    case 16:
      if (eof) ADVANCE(18);
      ADVANCE_MAP(
        '#', 27,
        '(', 22,
        '-', 3,
        '/', 4,
        ':', 14,
        '=', 15,
        'S', 43,
        'd', 39,
        'p', 45,
        't', 41,
      );
      if (('\t' <= lookahead && lookahead <= '\r') ||
          lookahead == ' ') SKIP(16);
      if (lookahead == '\'' ||
          ('.' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z') ||
          lookahead == '_' ||
          ('a' <= lookahead && lookahead <= 'z')) ADVANCE(49);
      END_STATE();
    case 17:
      if (eof) ADVANCE(18);
      if (lookahead == '-') ADVANCE(2);
      if (lookahead == '/') ADVANCE(4);
      if (lookahead == 'd') ADVANCE(39);
      if (lookahead == 'p') ADVANCE(45);
      if (lookahead == 't') ADVANCE(41);
      if (('\t' <= lookahead && lookahead <= '\r') ||
          lookahead == ' ') SKIP(17);
      if (lookahead == '\'' ||
          ('.' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z') ||
          lookahead == '_' ||
          ('a' <= lookahead && lookahead <= 'z')) ADVANCE(49);
      END_STATE();
    case 18:
      ACCEPT_TOKEN(ts_builtin_sym_end);
      END_STATE();
    case 19:
      ACCEPT_TOKEN(anon_sym_COLON);
      END_STATE();
    case 20:
      ACCEPT_TOKEN(anon_sym_COLON);
      if (lookahead == '=') ADVANCE(21);
      END_STATE();
    case 21:
      ACCEPT_TOKEN(anon_sym_COLON_EQ);
      END_STATE();
    case 22:
      ACCEPT_TOKEN(anon_sym_LPAREN);
      END_STATE();
    case 23:
      ACCEPT_TOKEN(anon_sym_RPAREN);
      END_STATE();
    case 24:
      ACCEPT_TOKEN(anon_sym_EQ_GT);
      END_STATE();
    case 25:
      ACCEPT_TOKEN(anon_sym_DASH_GT);
      END_STATE();
    case 26:
      ACCEPT_TOKEN(anon_sym_Sort);
      if (lookahead == '\'' ||
          lookahead == '.' ||
          ('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z') ||
          lookahead == '_' ||
          ('a' <= lookahead && lookahead <= 'z')) ADVANCE(49);
      END_STATE();
    case 27:
      ACCEPT_TOKEN(anon_sym_POUND);
      END_STATE();
    case 28:
      ACCEPT_TOKEN(aux_sym_bound_var_token1);
      if (('0' <= lookahead && lookahead <= '9')) ADVANCE(28);
      if (lookahead == '\'' ||
          lookahead == '.' ||
          ('A' <= lookahead && lookahead <= 'Z') ||
          lookahead == '_' ||
          ('a' <= lookahead && lookahead <= 'z')) ADVANCE(49);
      END_STATE();
    case 29:
      ACCEPT_TOKEN(aux_sym_bound_var_token1);
      if (('0' <= lookahead && lookahead <= '9')) ADVANCE(29);
      END_STATE();
    case 30:
      ACCEPT_TOKEN(anon_sym_PLUS);
      END_STATE();
    case 31:
      ACCEPT_TOKEN(anon_sym_1);
      END_STATE();
    case 32:
      ACCEPT_TOKEN(anon_sym_1);
      if (('0' <= lookahead && lookahead <= '9')) ADVANCE(28);
      if (lookahead == '\'' ||
          lookahead == '.' ||
          ('A' <= lookahead && lookahead <= 'Z') ||
          lookahead == '_' ||
          ('a' <= lookahead && lookahead <= 'z')) ADVANCE(49);
      END_STATE();
    case 33:
      ACCEPT_TOKEN(anon_sym_Max);
      if (lookahead == '\'' ||
          lookahead == '.' ||
          ('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z') ||
          lookahead == '_' ||
          ('a' <= lookahead && lookahead <= 'z')) ADVANCE(49);
      END_STATE();
    case 34:
      ACCEPT_TOKEN(anon_sym_COMMA);
      END_STATE();
    case 35:
      ACCEPT_TOKEN(anon_sym_IMax);
      if (lookahead == '\'' ||
          lookahead == '.' ||
          ('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z') ||
          lookahead == '_' ||
          ('a' <= lookahead && lookahead <= 'z')) ADVANCE(49);
      END_STATE();
    case 36:
      ACCEPT_TOKEN(sym_identifier);
      if (lookahead == 'M') ADVANCE(38);
      if (lookahead == '\'' ||
          lookahead == '.' ||
          ('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z') ||
          lookahead == '_' ||
          ('a' <= lookahead && lookahead <= 'z')) ADVANCE(49);
      END_STATE();
    case 37:
      ACCEPT_TOKEN(sym_identifier);
      if (lookahead == 'a') ADVANCE(47);
      if (lookahead == '\'' ||
          lookahead == '.' ||
          ('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z') ||
          lookahead == '_' ||
          ('b' <= lookahead && lookahead <= 'z')) ADVANCE(49);
      END_STATE();
    case 38:
      ACCEPT_TOKEN(sym_identifier);
      if (lookahead == 'a') ADVANCE(48);
      if (lookahead == '\'' ||
          lookahead == '.' ||
          ('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z') ||
          lookahead == '_' ||
          ('b' <= lookahead && lookahead <= 'z')) ADVANCE(49);
      END_STATE();
    case 39:
      ACCEPT_TOKEN(sym_identifier);
      if (lookahead == 'e') ADVANCE(40);
      if (lookahead == '\'' ||
          lookahead == '.' ||
          ('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z') ||
          lookahead == '_' ||
          ('a' <= lookahead && lookahead <= 'z')) ADVANCE(49);
      END_STATE();
    case 40:
      ACCEPT_TOKEN(sym_identifier);
      if (lookahead == 'f') ADVANCE(50);
      if (lookahead == '\'' ||
          lookahead == '.' ||
          ('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z') ||
          lookahead == '_' ||
          ('a' <= lookahead && lookahead <= 'z')) ADVANCE(49);
      END_STATE();
    case 41:
      ACCEPT_TOKEN(sym_identifier);
      if (lookahead == 'h') ADVANCE(42);
      if (lookahead == '\'' ||
          lookahead == '.' ||
          ('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z') ||
          lookahead == '_' ||
          ('a' <= lookahead && lookahead <= 'z')) ADVANCE(49);
      END_STATE();
    case 42:
      ACCEPT_TOKEN(sym_identifier);
      if (lookahead == 'm') ADVANCE(51);
      if (lookahead == '\'' ||
          lookahead == '.' ||
          ('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z') ||
          lookahead == '_' ||
          ('a' <= lookahead && lookahead <= 'z')) ADVANCE(49);
      END_STATE();
    case 43:
      ACCEPT_TOKEN(sym_identifier);
      if (lookahead == 'o') ADVANCE(44);
      if (lookahead == '\'' ||
          lookahead == '.' ||
          ('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z') ||
          lookahead == '_' ||
          ('a' <= lookahead && lookahead <= 'z')) ADVANCE(49);
      END_STATE();
    case 44:
      ACCEPT_TOKEN(sym_identifier);
      if (lookahead == 'r') ADVANCE(46);
      if (lookahead == '\'' ||
          lookahead == '.' ||
          ('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z') ||
          lookahead == '_' ||
          ('a' <= lookahead && lookahead <= 'z')) ADVANCE(49);
      END_STATE();
    case 45:
      ACCEPT_TOKEN(sym_identifier);
      if (lookahead == 's') ADVANCE(52);
      if (lookahead == '\'' ||
          lookahead == '.' ||
          ('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z') ||
          lookahead == '_' ||
          ('a' <= lookahead && lookahead <= 'z')) ADVANCE(49);
      END_STATE();
    case 46:
      ACCEPT_TOKEN(sym_identifier);
      if (lookahead == 't') ADVANCE(26);
      if (lookahead == '\'' ||
          lookahead == '.' ||
          ('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z') ||
          lookahead == '_' ||
          ('a' <= lookahead && lookahead <= 'z')) ADVANCE(49);
      END_STATE();
    case 47:
      ACCEPT_TOKEN(sym_identifier);
      if (lookahead == 'x') ADVANCE(33);
      if (lookahead == '\'' ||
          lookahead == '.' ||
          ('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z') ||
          lookahead == '_' ||
          ('a' <= lookahead && lookahead <= 'z')) ADVANCE(49);
      END_STATE();
    case 48:
      ACCEPT_TOKEN(sym_identifier);
      if (lookahead == 'x') ADVANCE(35);
      if (lookahead == '\'' ||
          lookahead == '.' ||
          ('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z') ||
          lookahead == '_' ||
          ('a' <= lookahead && lookahead <= 'z')) ADVANCE(49);
      END_STATE();
    case 49:
      ACCEPT_TOKEN(sym_identifier);
      if (lookahead == '\'' ||
          lookahead == '.' ||
          ('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z') ||
          lookahead == '_' ||
          ('a' <= lookahead && lookahead <= 'z')) ADVANCE(49);
      END_STATE();
    case 50:
      ACCEPT_TOKEN(sym_def_key);
      END_STATE();
    case 51:
      ACCEPT_TOKEN(sym_thm_key);
      END_STATE();
    case 52:
      ACCEPT_TOKEN(sym_ps_key);
      END_STATE();
    case 53:
      ACCEPT_TOKEN(anon_sym_DASH_DASH);
      END_STATE();
    case 54:
      ACCEPT_TOKEN(anon_sym_DASH_DASH);
      if (lookahead == '-') ADVANCE(13);
      if (lookahead != 0) ADVANCE(8);
      END_STATE();
    case 55:
      ACCEPT_TOKEN(anon_sym_DASH_DASH);
      if (lookahead != 0 &&
          lookahead != '\n') ADVANCE(59);
      END_STATE();
    case 56:
      ACCEPT_TOKEN(aux_sym_comment_token1);
      if (lookahead == '-') ADVANCE(57);
      if (lookahead == '/') ADVANCE(58);
      if (lookahead == '\t' ||
          (0x0b <= lookahead && lookahead <= '\r') ||
          lookahead == ' ') ADVANCE(56);
      if (lookahead != 0 &&
          (lookahead < '\t' || '\r' < lookahead)) ADVANCE(59);
      END_STATE();
    case 57:
      ACCEPT_TOKEN(aux_sym_comment_token1);
      if (lookahead == '-') ADVANCE(55);
      if (lookahead != 0 &&
          lookahead != '\n') ADVANCE(59);
      END_STATE();
    case 58:
      ACCEPT_TOKEN(aux_sym_comment_token1);
      if (lookahead == '-') ADVANCE(62);
      if (lookahead != 0 &&
          lookahead != '\n') ADVANCE(59);
      END_STATE();
    case 59:
      ACCEPT_TOKEN(aux_sym_comment_token1);
      if (lookahead != 0 &&
          lookahead != '\n') ADVANCE(59);
      END_STATE();
    case 60:
      ACCEPT_TOKEN(anon_sym_SLASH_DASH);
      END_STATE();
    case 61:
      ACCEPT_TOKEN(anon_sym_SLASH_DASH);
      if (lookahead == '/') ADVANCE(63);
      if (lookahead != 0) ADVANCE(8);
      END_STATE();
    case 62:
      ACCEPT_TOKEN(anon_sym_SLASH_DASH);
      if (lookahead != 0 &&
          lookahead != '\n') ADVANCE(59);
      END_STATE();
    case 63:
      ACCEPT_TOKEN(aux_sym_comment_token2);
      END_STATE();
    default:
      return false;
  }
}

static const TSLexMode ts_lex_modes[STATE_COUNT] = {
  [0] = {.lex_state = 0},
  [1] = {.lex_state = 0},
  [2] = {.lex_state = 16},
  [3] = {.lex_state = 16},
  [4] = {.lex_state = 16},
  [5] = {.lex_state = 16},
  [6] = {.lex_state = 16},
  [7] = {.lex_state = 16},
  [8] = {.lex_state = 16},
  [9] = {.lex_state = 16},
  [10] = {.lex_state = 16},
  [11] = {.lex_state = 16},
  [12] = {.lex_state = 1},
  [13] = {.lex_state = 1},
  [14] = {.lex_state = 1},
  [15] = {.lex_state = 1},
  [16] = {.lex_state = 1},
  [17] = {.lex_state = 1},
  [18] = {.lex_state = 1},
  [19] = {.lex_state = 1},
  [20] = {.lex_state = 1},
  [21] = {.lex_state = 1},
  [22] = {.lex_state = 1},
  [23] = {.lex_state = 1},
  [24] = {.lex_state = 1},
  [25] = {.lex_state = 1},
  [26] = {.lex_state = 1},
  [27] = {.lex_state = 1},
  [28] = {.lex_state = 1},
  [29] = {.lex_state = 1},
  [30] = {.lex_state = 0},
  [31] = {.lex_state = 0},
  [32] = {.lex_state = 16},
  [33] = {.lex_state = 16},
  [34] = {.lex_state = 16},
  [35] = {.lex_state = 16},
  [36] = {.lex_state = 16},
  [37] = {.lex_state = 16},
  [38] = {.lex_state = 1},
  [39] = {.lex_state = 1},
  [40] = {.lex_state = 1},
  [41] = {.lex_state = 1},
  [42] = {.lex_state = 1},
  [43] = {.lex_state = 1},
  [44] = {.lex_state = 1},
  [45] = {.lex_state = 10},
  [46] = {.lex_state = 10},
  [47] = {.lex_state = 10},
  [48] = {.lex_state = 17},
  [49] = {.lex_state = 17},
  [50] = {.lex_state = 10},
  [51] = {.lex_state = 0},
  [52] = {.lex_state = 0},
  [53] = {.lex_state = 0},
  [54] = {.lex_state = 0},
  [55] = {.lex_state = 0},
  [56] = {.lex_state = 0},
  [57] = {.lex_state = 0},
  [58] = {.lex_state = 0},
  [59] = {.lex_state = 0},
  [60] = {.lex_state = 0},
  [61] = {.lex_state = 0},
  [62] = {.lex_state = 0},
  [63] = {.lex_state = 11},
  [64] = {.lex_state = 0},
  [65] = {.lex_state = 11},
  [66] = {.lex_state = 5},
  [67] = {.lex_state = 0},
  [68] = {.lex_state = 0},
  [69] = {.lex_state = 56},
  [70] = {.lex_state = 12},
  [71] = {.lex_state = 0},
  [72] = {.lex_state = 0},
  [73] = {.lex_state = 0},
  [74] = {.lex_state = 12},
  [75] = {.lex_state = 0},
  [76] = {.lex_state = 9},
  [77] = {.lex_state = 0},
  [78] = {(TSStateId)(-1)},
};

static const uint16_t ts_parse_table[LARGE_STATE_COUNT][SYMBOL_COUNT] = {
  [0] = {
    [sym_comment] = STATE(0),
    [ts_builtin_sym_end] = ACTIONS(1),
    [anon_sym_COLON] = ACTIONS(1),
    [anon_sym_COLON_EQ] = ACTIONS(1),
    [anon_sym_LPAREN] = ACTIONS(1),
    [anon_sym_RPAREN] = ACTIONS(1),
    [anon_sym_EQ_GT] = ACTIONS(1),
    [anon_sym_DASH_GT] = ACTIONS(1),
    [anon_sym_Sort] = ACTIONS(1),
    [anon_sym_POUND] = ACTIONS(1),
    [aux_sym_bound_var_token1] = ACTIONS(1),
    [anon_sym_PLUS] = ACTIONS(1),
    [anon_sym_1] = ACTIONS(1),
    [anon_sym_Max] = ACTIONS(1),
    [anon_sym_COMMA] = ACTIONS(1),
    [anon_sym_IMax] = ACTIONS(1),
    [sym_identifier] = ACTIONS(1),
    [sym_def_key] = ACTIONS(1),
    [sym_thm_key] = ACTIONS(1),
    [sym_ps_key] = ACTIONS(1),
    [anon_sym_DASH_DASH] = ACTIONS(3),
    [anon_sym_SLASH_DASH] = ACTIONS(5),
  },
  [1] = {
    [sym_start] = STATE(67),
    [sym_command] = STATE(51),
    [sym_definition] = STATE(52),
    [sym_theorem] = STATE(52),
    [sym_proofstep] = STATE(52),
    [sym_action] = STATE(11),
    [sym_search] = STATE(48),
    [sym_comment] = STATE(1),
    [aux_sym_start_repeat1] = STATE(30),
    [ts_builtin_sym_end] = ACTIONS(7),
    [sym_def_key] = ACTIONS(9),
    [sym_thm_key] = ACTIONS(11),
    [sym_ps_key] = ACTIONS(13),
    [anon_sym_DASH_DASH] = ACTIONS(3),
    [anon_sym_SLASH_DASH] = ACTIONS(5),
  },
  [2] = {
    [sym_expr] = STATE(2),
    [sym_primary] = STATE(37),
    [sym_app] = STATE(37),
    [sym_lambda] = STATE(37),
    [sym_lambda_arg] = STATE(73),
    [sym_forall] = STATE(37),
    [sym_forall_arg] = STATE(75),
    [sym_sort] = STATE(33),
    [sym_const] = STATE(33),
    [sym_bound_var] = STATE(33),
    [sym_comment] = STATE(2),
    [ts_builtin_sym_end] = ACTIONS(15),
    [anon_sym_COLON_EQ] = ACTIONS(15),
    [anon_sym_LPAREN] = ACTIONS(15),
    [anon_sym_EQ_GT] = ACTIONS(15),
    [anon_sym_DASH_GT] = ACTIONS(15),
    [anon_sym_Sort] = ACTIONS(17),
    [anon_sym_POUND] = ACTIONS(15),
    [sym_identifier] = ACTIONS(17),
    [sym_def_key] = ACTIONS(15),
    [sym_thm_key] = ACTIONS(15),
    [sym_ps_key] = ACTIONS(15),
    [anon_sym_DASH_DASH] = ACTIONS(3),
    [anon_sym_SLASH_DASH] = ACTIONS(5),
  },
  [3] = {
    [sym_expr] = STATE(2),
    [sym_primary] = STATE(37),
    [sym_app] = STATE(37),
    [sym_lambda] = STATE(37),
    [sym_lambda_arg] = STATE(73),
    [sym_forall] = STATE(37),
    [sym_forall_arg] = STATE(75),
    [sym_sort] = STATE(33),
    [sym_const] = STATE(33),
    [sym_bound_var] = STATE(33),
    [sym_comment] = STATE(3),
    [ts_builtin_sym_end] = ACTIONS(19),
    [anon_sym_COLON_EQ] = ACTIONS(19),
    [anon_sym_LPAREN] = ACTIONS(21),
    [anon_sym_EQ_GT] = ACTIONS(19),
    [anon_sym_DASH_GT] = ACTIONS(19),
    [anon_sym_Sort] = ACTIONS(23),
    [anon_sym_POUND] = ACTIONS(25),
    [sym_identifier] = ACTIONS(27),
    [sym_def_key] = ACTIONS(19),
    [sym_thm_key] = ACTIONS(19),
    [sym_ps_key] = ACTIONS(19),
    [anon_sym_DASH_DASH] = ACTIONS(3),
    [anon_sym_SLASH_DASH] = ACTIONS(5),
  },
  [4] = {
    [sym_expr] = STATE(2),
    [sym_primary] = STATE(37),
    [sym_app] = STATE(37),
    [sym_lambda] = STATE(37),
    [sym_lambda_arg] = STATE(73),
    [sym_forall] = STATE(37),
    [sym_forall_arg] = STATE(75),
    [sym_sort] = STATE(33),
    [sym_const] = STATE(33),
    [sym_bound_var] = STATE(33),
    [sym_comment] = STATE(4),
    [ts_builtin_sym_end] = ACTIONS(29),
    [anon_sym_COLON_EQ] = ACTIONS(29),
    [anon_sym_LPAREN] = ACTIONS(21),
    [anon_sym_EQ_GT] = ACTIONS(29),
    [anon_sym_DASH_GT] = ACTIONS(29),
    [anon_sym_Sort] = ACTIONS(23),
    [anon_sym_POUND] = ACTIONS(25),
    [sym_identifier] = ACTIONS(27),
    [sym_def_key] = ACTIONS(29),
    [sym_thm_key] = ACTIONS(29),
    [sym_ps_key] = ACTIONS(29),
    [anon_sym_DASH_DASH] = ACTIONS(3),
    [anon_sym_SLASH_DASH] = ACTIONS(5),
  },
  [5] = {
    [sym_expr] = STATE(2),
    [sym_primary] = STATE(37),
    [sym_app] = STATE(37),
    [sym_lambda] = STATE(37),
    [sym_lambda_arg] = STATE(73),
    [sym_forall] = STATE(37),
    [sym_forall_arg] = STATE(75),
    [sym_sort] = STATE(33),
    [sym_const] = STATE(33),
    [sym_bound_var] = STATE(33),
    [sym_comment] = STATE(5),
    [ts_builtin_sym_end] = ACTIONS(31),
    [anon_sym_COLON_EQ] = ACTIONS(33),
    [anon_sym_LPAREN] = ACTIONS(21),
    [anon_sym_EQ_GT] = ACTIONS(35),
    [anon_sym_DASH_GT] = ACTIONS(37),
    [anon_sym_Sort] = ACTIONS(23),
    [anon_sym_POUND] = ACTIONS(25),
    [sym_identifier] = ACTIONS(27),
    [sym_def_key] = ACTIONS(31),
    [sym_thm_key] = ACTIONS(31),
    [sym_ps_key] = ACTIONS(31),
    [anon_sym_DASH_DASH] = ACTIONS(3),
    [anon_sym_SLASH_DASH] = ACTIONS(5),
  },
  [6] = {
    [sym_expr] = STATE(2),
    [sym_primary] = STATE(37),
    [sym_app] = STATE(37),
    [sym_lambda] = STATE(37),
    [sym_lambda_arg] = STATE(73),
    [sym_forall] = STATE(37),
    [sym_forall_arg] = STATE(75),
    [sym_sort] = STATE(33),
    [sym_const] = STATE(33),
    [sym_bound_var] = STATE(33),
    [sym_comment] = STATE(6),
    [ts_builtin_sym_end] = ACTIONS(39),
    [anon_sym_LPAREN] = ACTIONS(21),
    [anon_sym_EQ_GT] = ACTIONS(35),
    [anon_sym_DASH_GT] = ACTIONS(37),
    [anon_sym_Sort] = ACTIONS(23),
    [anon_sym_POUND] = ACTIONS(25),
    [sym_identifier] = ACTIONS(27),
    [sym_def_key] = ACTIONS(39),
    [sym_thm_key] = ACTIONS(39),
    [sym_ps_key] = ACTIONS(39),
    [anon_sym_DASH_DASH] = ACTIONS(3),
    [anon_sym_SLASH_DASH] = ACTIONS(5),
  },
  [7] = {
    [sym_expr] = STATE(2),
    [sym_primary] = STATE(37),
    [sym_app] = STATE(37),
    [sym_lambda] = STATE(37),
    [sym_lambda_arg] = STATE(73),
    [sym_forall] = STATE(37),
    [sym_forall_arg] = STATE(75),
    [sym_sort] = STATE(33),
    [sym_const] = STATE(33),
    [sym_bound_var] = STATE(33),
    [sym_comment] = STATE(7),
    [ts_builtin_sym_end] = ACTIONS(41),
    [anon_sym_LPAREN] = ACTIONS(21),
    [anon_sym_EQ_GT] = ACTIONS(35),
    [anon_sym_DASH_GT] = ACTIONS(37),
    [anon_sym_Sort] = ACTIONS(23),
    [anon_sym_POUND] = ACTIONS(25),
    [sym_identifier] = ACTIONS(27),
    [sym_def_key] = ACTIONS(41),
    [sym_thm_key] = ACTIONS(41),
    [sym_ps_key] = ACTIONS(41),
    [anon_sym_DASH_DASH] = ACTIONS(3),
    [anon_sym_SLASH_DASH] = ACTIONS(5),
  },
  [8] = {
    [sym_expr] = STATE(2),
    [sym_primary] = STATE(37),
    [sym_app] = STATE(37),
    [sym_lambda] = STATE(37),
    [sym_lambda_arg] = STATE(73),
    [sym_forall] = STATE(37),
    [sym_forall_arg] = STATE(75),
    [sym_sort] = STATE(33),
    [sym_const] = STATE(33),
    [sym_bound_var] = STATE(33),
    [sym_comment] = STATE(8),
    [ts_builtin_sym_end] = ACTIONS(43),
    [anon_sym_LPAREN] = ACTIONS(21),
    [anon_sym_EQ_GT] = ACTIONS(35),
    [anon_sym_DASH_GT] = ACTIONS(37),
    [anon_sym_Sort] = ACTIONS(23),
    [anon_sym_POUND] = ACTIONS(25),
    [sym_identifier] = ACTIONS(27),
    [sym_def_key] = ACTIONS(43),
    [sym_thm_key] = ACTIONS(43),
    [sym_ps_key] = ACTIONS(43),
    [anon_sym_DASH_DASH] = ACTIONS(3),
    [anon_sym_SLASH_DASH] = ACTIONS(5),
  },
  [9] = {
    [sym_expr] = STATE(2),
    [sym_primary] = STATE(37),
    [sym_app] = STATE(37),
    [sym_lambda] = STATE(37),
    [sym_lambda_arg] = STATE(73),
    [sym_forall] = STATE(37),
    [sym_forall_arg] = STATE(75),
    [sym_sort] = STATE(33),
    [sym_const] = STATE(33),
    [sym_bound_var] = STATE(33),
    [sym_comment] = STATE(9),
    [ts_builtin_sym_end] = ACTIONS(45),
    [anon_sym_LPAREN] = ACTIONS(21),
    [anon_sym_EQ_GT] = ACTIONS(35),
    [anon_sym_DASH_GT] = ACTIONS(37),
    [anon_sym_Sort] = ACTIONS(23),
    [anon_sym_POUND] = ACTIONS(25),
    [sym_identifier] = ACTIONS(27),
    [sym_def_key] = ACTIONS(45),
    [sym_thm_key] = ACTIONS(45),
    [sym_ps_key] = ACTIONS(45),
    [anon_sym_DASH_DASH] = ACTIONS(3),
    [anon_sym_SLASH_DASH] = ACTIONS(5),
  },
  [10] = {
    [sym_expr] = STATE(2),
    [sym_primary] = STATE(37),
    [sym_app] = STATE(37),
    [sym_lambda] = STATE(37),
    [sym_lambda_arg] = STATE(73),
    [sym_forall] = STATE(37),
    [sym_forall_arg] = STATE(75),
    [sym_sort] = STATE(33),
    [sym_const] = STATE(33),
    [sym_bound_var] = STATE(33),
    [sym_comment] = STATE(10),
    [ts_builtin_sym_end] = ACTIONS(31),
    [anon_sym_LPAREN] = ACTIONS(21),
    [anon_sym_EQ_GT] = ACTIONS(35),
    [anon_sym_DASH_GT] = ACTIONS(37),
    [anon_sym_Sort] = ACTIONS(23),
    [anon_sym_POUND] = ACTIONS(25),
    [sym_identifier] = ACTIONS(27),
    [sym_def_key] = ACTIONS(31),
    [sym_thm_key] = ACTIONS(31),
    [sym_ps_key] = ACTIONS(31),
    [anon_sym_DASH_DASH] = ACTIONS(3),
    [anon_sym_SLASH_DASH] = ACTIONS(5),
  },
};

static const uint16_t ts_small_parse_table[] = {
  [0] = 13,
    ACTIONS(3), 1,
      anon_sym_DASH_DASH,
    ACTIONS(5), 1,
      anon_sym_SLASH_DASH,
    ACTIONS(21), 1,
      anon_sym_LPAREN,
    ACTIONS(23), 1,
      anon_sym_Sort,
    ACTIONS(25), 1,
      anon_sym_POUND,
    ACTIONS(27), 1,
      sym_identifier,
    STATE(9), 1,
      sym_expr,
    STATE(11), 1,
      sym_comment,
    STATE(73), 1,
      sym_lambda_arg,
    STATE(75), 1,
      sym_forall_arg,
    STATE(33), 3,
      sym_sort,
      sym_const,
      sym_bound_var,
    ACTIONS(47), 4,
      ts_builtin_sym_end,
      sym_def_key,
      sym_thm_key,
      sym_ps_key,
    STATE(37), 4,
      sym_primary,
      sym_app,
      sym_lambda,
      sym_forall,
  [48] = 15,
    ACTIONS(3), 1,
      anon_sym_DASH_DASH,
    ACTIONS(5), 1,
      anon_sym_SLASH_DASH,
    ACTIONS(35), 1,
      anon_sym_EQ_GT,
    ACTIONS(37), 1,
      anon_sym_DASH_GT,
    ACTIONS(49), 1,
      anon_sym_LPAREN,
    ACTIONS(51), 1,
      anon_sym_RPAREN,
    ACTIONS(53), 1,
      anon_sym_Sort,
    ACTIONS(55), 1,
      anon_sym_POUND,
    ACTIONS(57), 1,
      sym_identifier,
    STATE(12), 1,
      sym_comment,
    STATE(15), 1,
      sym_expr,
    STATE(71), 1,
      sym_lambda_arg,
    STATE(72), 1,
      sym_forall_arg,
    STATE(43), 3,
      sym_sort,
      sym_const,
      sym_bound_var,
    STATE(41), 4,
      sym_primary,
      sym_app,
      sym_lambda,
      sym_forall,
  [99] = 15,
    ACTIONS(3), 1,
      anon_sym_DASH_DASH,
    ACTIONS(5), 1,
      anon_sym_SLASH_DASH,
    ACTIONS(35), 1,
      anon_sym_EQ_GT,
    ACTIONS(37), 1,
      anon_sym_DASH_GT,
    ACTIONS(49), 1,
      anon_sym_LPAREN,
    ACTIONS(53), 1,
      anon_sym_Sort,
    ACTIONS(55), 1,
      anon_sym_POUND,
    ACTIONS(57), 1,
      sym_identifier,
    ACTIONS(59), 1,
      anon_sym_RPAREN,
    STATE(13), 1,
      sym_comment,
    STATE(15), 1,
      sym_expr,
    STATE(71), 1,
      sym_lambda_arg,
    STATE(72), 1,
      sym_forall_arg,
    STATE(43), 3,
      sym_sort,
      sym_const,
      sym_bound_var,
    STATE(41), 4,
      sym_primary,
      sym_app,
      sym_lambda,
      sym_forall,
  [150] = 15,
    ACTIONS(3), 1,
      anon_sym_DASH_DASH,
    ACTIONS(5), 1,
      anon_sym_SLASH_DASH,
    ACTIONS(35), 1,
      anon_sym_EQ_GT,
    ACTIONS(37), 1,
      anon_sym_DASH_GT,
    ACTIONS(49), 1,
      anon_sym_LPAREN,
    ACTIONS(53), 1,
      anon_sym_Sort,
    ACTIONS(55), 1,
      anon_sym_POUND,
    ACTIONS(57), 1,
      sym_identifier,
    ACTIONS(61), 1,
      anon_sym_RPAREN,
    STATE(14), 1,
      sym_comment,
    STATE(15), 1,
      sym_expr,
    STATE(71), 1,
      sym_lambda_arg,
    STATE(72), 1,
      sym_forall_arg,
    STATE(43), 3,
      sym_sort,
      sym_const,
      sym_bound_var,
    STATE(41), 4,
      sym_primary,
      sym_app,
      sym_lambda,
      sym_forall,
  [201] = 9,
    ACTIONS(3), 1,
      anon_sym_DASH_DASH,
    ACTIONS(5), 1,
      anon_sym_SLASH_DASH,
    STATE(71), 1,
      sym_lambda_arg,
    STATE(72), 1,
      sym_forall_arg,
    ACTIONS(17), 2,
      anon_sym_Sort,
      sym_identifier,
    STATE(15), 2,
      sym_expr,
      sym_comment,
    STATE(43), 3,
      sym_sort,
      sym_const,
      sym_bound_var,
    STATE(41), 4,
      sym_primary,
      sym_app,
      sym_lambda,
      sym_forall,
    ACTIONS(15), 5,
      anon_sym_LPAREN,
      anon_sym_RPAREN,
      anon_sym_EQ_GT,
      anon_sym_DASH_GT,
      anon_sym_POUND,
  [240] = 13,
    ACTIONS(3), 1,
      anon_sym_DASH_DASH,
    ACTIONS(5), 1,
      anon_sym_SLASH_DASH,
    ACTIONS(49), 1,
      anon_sym_LPAREN,
    ACTIONS(53), 1,
      anon_sym_Sort,
    ACTIONS(55), 1,
      anon_sym_POUND,
    ACTIONS(57), 1,
      sym_identifier,
    STATE(15), 1,
      sym_expr,
    STATE(16), 1,
      sym_comment,
    STATE(71), 1,
      sym_lambda_arg,
    STATE(72), 1,
      sym_forall_arg,
    ACTIONS(19), 3,
      anon_sym_RPAREN,
      anon_sym_EQ_GT,
      anon_sym_DASH_GT,
    STATE(43), 3,
      sym_sort,
      sym_const,
      sym_bound_var,
    STATE(41), 4,
      sym_primary,
      sym_app,
      sym_lambda,
      sym_forall,
  [287] = 13,
    ACTIONS(3), 1,
      anon_sym_DASH_DASH,
    ACTIONS(5), 1,
      anon_sym_SLASH_DASH,
    ACTIONS(49), 1,
      anon_sym_LPAREN,
    ACTIONS(53), 1,
      anon_sym_Sort,
    ACTIONS(55), 1,
      anon_sym_POUND,
    ACTIONS(57), 1,
      sym_identifier,
    STATE(15), 1,
      sym_expr,
    STATE(17), 1,
      sym_comment,
    STATE(71), 1,
      sym_lambda_arg,
    STATE(72), 1,
      sym_forall_arg,
    ACTIONS(29), 3,
      anon_sym_RPAREN,
      anon_sym_EQ_GT,
      anon_sym_DASH_GT,
    STATE(43), 3,
      sym_sort,
      sym_const,
      sym_bound_var,
    STATE(41), 4,
      sym_primary,
      sym_app,
      sym_lambda,
      sym_forall,
  [334] = 12,
    ACTIONS(3), 1,
      anon_sym_DASH_DASH,
    ACTIONS(5), 1,
      anon_sym_SLASH_DASH,
    ACTIONS(21), 1,
      anon_sym_LPAREN,
    ACTIONS(23), 1,
      anon_sym_Sort,
    ACTIONS(25), 1,
      anon_sym_POUND,
    ACTIONS(27), 1,
      sym_identifier,
    STATE(3), 1,
      sym_expr,
    STATE(18), 1,
      sym_comment,
    STATE(73), 1,
      sym_lambda_arg,
    STATE(75), 1,
      sym_forall_arg,
    STATE(33), 3,
      sym_sort,
      sym_const,
      sym_bound_var,
    STATE(37), 4,
      sym_primary,
      sym_app,
      sym_lambda,
      sym_forall,
  [376] = 12,
    ACTIONS(3), 1,
      anon_sym_DASH_DASH,
    ACTIONS(5), 1,
      anon_sym_SLASH_DASH,
    ACTIONS(49), 1,
      anon_sym_LPAREN,
    ACTIONS(53), 1,
      anon_sym_Sort,
    ACTIONS(55), 1,
      anon_sym_POUND,
    ACTIONS(57), 1,
      sym_identifier,
    STATE(13), 1,
      sym_expr,
    STATE(19), 1,
      sym_comment,
    STATE(71), 1,
      sym_lambda_arg,
    STATE(72), 1,
      sym_forall_arg,
    STATE(43), 3,
      sym_sort,
      sym_const,
      sym_bound_var,
    STATE(41), 4,
      sym_primary,
      sym_app,
      sym_lambda,
      sym_forall,
  [418] = 12,
    ACTIONS(3), 1,
      anon_sym_DASH_DASH,
    ACTIONS(5), 1,
      anon_sym_SLASH_DASH,
    ACTIONS(21), 1,
      anon_sym_LPAREN,
    ACTIONS(23), 1,
      anon_sym_Sort,
    ACTIONS(25), 1,
      anon_sym_POUND,
    ACTIONS(27), 1,
      sym_identifier,
    STATE(10), 1,
      sym_expr,
    STATE(20), 1,
      sym_comment,
    STATE(73), 1,
      sym_lambda_arg,
    STATE(75), 1,
      sym_forall_arg,
    STATE(33), 3,
      sym_sort,
      sym_const,
      sym_bound_var,
    STATE(37), 4,
      sym_primary,
      sym_app,
      sym_lambda,
      sym_forall,
  [460] = 12,
    ACTIONS(3), 1,
      anon_sym_DASH_DASH,
    ACTIONS(5), 1,
      anon_sym_SLASH_DASH,
    ACTIONS(21), 1,
      anon_sym_LPAREN,
    ACTIONS(23), 1,
      anon_sym_Sort,
    ACTIONS(25), 1,
      anon_sym_POUND,
    ACTIONS(27), 1,
      sym_identifier,
    STATE(8), 1,
      sym_expr,
    STATE(21), 1,
      sym_comment,
    STATE(73), 1,
      sym_lambda_arg,
    STATE(75), 1,
      sym_forall_arg,
    STATE(33), 3,
      sym_sort,
      sym_const,
      sym_bound_var,
    STATE(37), 4,
      sym_primary,
      sym_app,
      sym_lambda,
      sym_forall,
  [502] = 12,
    ACTIONS(3), 1,
      anon_sym_DASH_DASH,
    ACTIONS(5), 1,
      anon_sym_SLASH_DASH,
    ACTIONS(21), 1,
      anon_sym_LPAREN,
    ACTIONS(23), 1,
      anon_sym_Sort,
    ACTIONS(25), 1,
      anon_sym_POUND,
    ACTIONS(27), 1,
      sym_identifier,
    STATE(5), 1,
      sym_expr,
    STATE(22), 1,
      sym_comment,
    STATE(73), 1,
      sym_lambda_arg,
    STATE(75), 1,
      sym_forall_arg,
    STATE(33), 3,
      sym_sort,
      sym_const,
      sym_bound_var,
    STATE(37), 4,
      sym_primary,
      sym_app,
      sym_lambda,
      sym_forall,
  [544] = 12,
    ACTIONS(3), 1,
      anon_sym_DASH_DASH,
    ACTIONS(5), 1,
      anon_sym_SLASH_DASH,
    ACTIONS(21), 1,
      anon_sym_LPAREN,
    ACTIONS(23), 1,
      anon_sym_Sort,
    ACTIONS(25), 1,
      anon_sym_POUND,
    ACTIONS(27), 1,
      sym_identifier,
    STATE(6), 1,
      sym_expr,
    STATE(23), 1,
      sym_comment,
    STATE(73), 1,
      sym_lambda_arg,
    STATE(75), 1,
      sym_forall_arg,
    STATE(33), 3,
      sym_sort,
      sym_const,
      sym_bound_var,
    STATE(37), 4,
      sym_primary,
      sym_app,
      sym_lambda,
      sym_forall,
  [586] = 12,
    ACTIONS(3), 1,
      anon_sym_DASH_DASH,
    ACTIONS(5), 1,
      anon_sym_SLASH_DASH,
    ACTIONS(49), 1,
      anon_sym_LPAREN,
    ACTIONS(53), 1,
      anon_sym_Sort,
    ACTIONS(55), 1,
      anon_sym_POUND,
    ACTIONS(57), 1,
      sym_identifier,
    STATE(17), 1,
      sym_expr,
    STATE(24), 1,
      sym_comment,
    STATE(71), 1,
      sym_lambda_arg,
    STATE(72), 1,
      sym_forall_arg,
    STATE(43), 3,
      sym_sort,
      sym_const,
      sym_bound_var,
    STATE(41), 4,
      sym_primary,
      sym_app,
      sym_lambda,
      sym_forall,
  [628] = 13,
    ACTIONS(3), 1,
      anon_sym_DASH_DASH,
    ACTIONS(5), 1,
      anon_sym_SLASH_DASH,
    ACTIONS(49), 1,
      anon_sym_LPAREN,
    ACTIONS(53), 1,
      anon_sym_Sort,
    ACTIONS(55), 1,
      anon_sym_POUND,
    ACTIONS(57), 1,
      sym_identifier,
    STATE(12), 1,
      sym_expr,
    STATE(25), 1,
      sym_comment,
    STATE(39), 1,
      sym_const,
    STATE(71), 1,
      sym_lambda_arg,
    STATE(72), 1,
      sym_forall_arg,
    STATE(43), 2,
      sym_sort,
      sym_bound_var,
    STATE(41), 4,
      sym_primary,
      sym_app,
      sym_lambda,
      sym_forall,
  [672] = 12,
    ACTIONS(3), 1,
      anon_sym_DASH_DASH,
    ACTIONS(5), 1,
      anon_sym_SLASH_DASH,
    ACTIONS(49), 1,
      anon_sym_LPAREN,
    ACTIONS(53), 1,
      anon_sym_Sort,
    ACTIONS(55), 1,
      anon_sym_POUND,
    ACTIONS(57), 1,
      sym_identifier,
    STATE(16), 1,
      sym_expr,
    STATE(26), 1,
      sym_comment,
    STATE(71), 1,
      sym_lambda_arg,
    STATE(72), 1,
      sym_forall_arg,
    STATE(43), 3,
      sym_sort,
      sym_const,
      sym_bound_var,
    STATE(41), 4,
      sym_primary,
      sym_app,
      sym_lambda,
      sym_forall,
  [714] = 12,
    ACTIONS(3), 1,
      anon_sym_DASH_DASH,
    ACTIONS(5), 1,
      anon_sym_SLASH_DASH,
    ACTIONS(21), 1,
      anon_sym_LPAREN,
    ACTIONS(23), 1,
      anon_sym_Sort,
    ACTIONS(25), 1,
      anon_sym_POUND,
    ACTIONS(27), 1,
      sym_identifier,
    STATE(7), 1,
      sym_expr,
    STATE(27), 1,
      sym_comment,
    STATE(73), 1,
      sym_lambda_arg,
    STATE(75), 1,
      sym_forall_arg,
    STATE(33), 3,
      sym_sort,
      sym_const,
      sym_bound_var,
    STATE(37), 4,
      sym_primary,
      sym_app,
      sym_lambda,
      sym_forall,
  [756] = 12,
    ACTIONS(3), 1,
      anon_sym_DASH_DASH,
    ACTIONS(5), 1,
      anon_sym_SLASH_DASH,
    ACTIONS(21), 1,
      anon_sym_LPAREN,
    ACTIONS(23), 1,
      anon_sym_Sort,
    ACTIONS(25), 1,
      anon_sym_POUND,
    ACTIONS(27), 1,
      sym_identifier,
    STATE(4), 1,
      sym_expr,
    STATE(28), 1,
      sym_comment,
    STATE(73), 1,
      sym_lambda_arg,
    STATE(75), 1,
      sym_forall_arg,
    STATE(33), 3,
      sym_sort,
      sym_const,
      sym_bound_var,
    STATE(37), 4,
      sym_primary,
      sym_app,
      sym_lambda,
      sym_forall,
  [798] = 13,
    ACTIONS(3), 1,
      anon_sym_DASH_DASH,
    ACTIONS(5), 1,
      anon_sym_SLASH_DASH,
    ACTIONS(49), 1,
      anon_sym_LPAREN,
    ACTIONS(53), 1,
      anon_sym_Sort,
    ACTIONS(55), 1,
      anon_sym_POUND,
    ACTIONS(57), 1,
      sym_identifier,
    STATE(14), 1,
      sym_expr,
    STATE(29), 1,
      sym_comment,
    STATE(39), 1,
      sym_const,
    STATE(71), 1,
      sym_lambda_arg,
    STATE(72), 1,
      sym_forall_arg,
    STATE(43), 2,
      sym_sort,
      sym_bound_var,
    STATE(41), 4,
      sym_primary,
      sym_app,
      sym_lambda,
      sym_forall,
  [842] = 12,
    ACTIONS(3), 1,
      anon_sym_DASH_DASH,
    ACTIONS(5), 1,
      anon_sym_SLASH_DASH,
    ACTIONS(9), 1,
      sym_def_key,
    ACTIONS(11), 1,
      sym_thm_key,
    ACTIONS(13), 1,
      sym_ps_key,
    ACTIONS(63), 1,
      ts_builtin_sym_end,
    STATE(11), 1,
      sym_action,
    STATE(30), 1,
      sym_comment,
    STATE(31), 1,
      aux_sym_start_repeat1,
    STATE(48), 1,
      sym_search,
    STATE(51), 1,
      sym_command,
    STATE(52), 3,
      sym_definition,
      sym_theorem,
      sym_proofstep,
  [881] = 11,
    ACTIONS(3), 1,
      anon_sym_DASH_DASH,
    ACTIONS(5), 1,
      anon_sym_SLASH_DASH,
    ACTIONS(65), 1,
      ts_builtin_sym_end,
    ACTIONS(67), 1,
      sym_def_key,
    ACTIONS(70), 1,
      sym_thm_key,
    ACTIONS(73), 1,
      sym_ps_key,
    STATE(11), 1,
      sym_action,
    STATE(48), 1,
      sym_search,
    STATE(51), 1,
      sym_command,
    STATE(31), 2,
      sym_comment,
      aux_sym_start_repeat1,
    STATE(52), 3,
      sym_definition,
      sym_theorem,
      sym_proofstep,
  [918] = 5,
    ACTIONS(3), 1,
      anon_sym_DASH_DASH,
    ACTIONS(5), 1,
      anon_sym_SLASH_DASH,
    STATE(32), 1,
      sym_comment,
    ACTIONS(78), 2,
      anon_sym_Sort,
      sym_identifier,
    ACTIONS(76), 9,
      ts_builtin_sym_end,
      anon_sym_COLON_EQ,
      anon_sym_LPAREN,
      anon_sym_EQ_GT,
      anon_sym_DASH_GT,
      anon_sym_POUND,
      sym_def_key,
      sym_thm_key,
      sym_ps_key,
  [943] = 5,
    ACTIONS(3), 1,
      anon_sym_DASH_DASH,
    ACTIONS(5), 1,
      anon_sym_SLASH_DASH,
    STATE(33), 1,
      sym_comment,
    ACTIONS(82), 2,
      anon_sym_Sort,
      sym_identifier,
    ACTIONS(80), 9,
      ts_builtin_sym_end,
      anon_sym_COLON_EQ,
      anon_sym_LPAREN,
      anon_sym_EQ_GT,
      anon_sym_DASH_GT,
      anon_sym_POUND,
      sym_def_key,
      sym_thm_key,
      sym_ps_key,
  [968] = 5,
    ACTIONS(3), 1,
      anon_sym_DASH_DASH,
    ACTIONS(5), 1,
      anon_sym_SLASH_DASH,
    STATE(34), 1,
      sym_comment,
    ACTIONS(86), 2,
      anon_sym_Sort,
      sym_identifier,
    ACTIONS(84), 9,
      ts_builtin_sym_end,
      anon_sym_COLON_EQ,
      anon_sym_LPAREN,
      anon_sym_EQ_GT,
      anon_sym_DASH_GT,
      anon_sym_POUND,
      sym_def_key,
      sym_thm_key,
      sym_ps_key,
  [993] = 5,
    ACTIONS(3), 1,
      anon_sym_DASH_DASH,
    ACTIONS(5), 1,
      anon_sym_SLASH_DASH,
    STATE(35), 1,
      sym_comment,
    ACTIONS(90), 2,
      anon_sym_Sort,
      sym_identifier,
    ACTIONS(88), 9,
      ts_builtin_sym_end,
      anon_sym_COLON_EQ,
      anon_sym_LPAREN,
      anon_sym_EQ_GT,
      anon_sym_DASH_GT,
      anon_sym_POUND,
      sym_def_key,
      sym_thm_key,
      sym_ps_key,
  [1018] = 5,
    ACTIONS(3), 1,
      anon_sym_DASH_DASH,
    ACTIONS(5), 1,
      anon_sym_SLASH_DASH,
    STATE(36), 1,
      sym_comment,
    ACTIONS(94), 2,
      anon_sym_Sort,
      sym_identifier,
    ACTIONS(92), 9,
      ts_builtin_sym_end,
      anon_sym_COLON_EQ,
      anon_sym_LPAREN,
      anon_sym_EQ_GT,
      anon_sym_DASH_GT,
      anon_sym_POUND,
      sym_def_key,
      sym_thm_key,
      sym_ps_key,
  [1043] = 5,
    ACTIONS(3), 1,
      anon_sym_DASH_DASH,
    ACTIONS(5), 1,
      anon_sym_SLASH_DASH,
    STATE(37), 1,
      sym_comment,
    ACTIONS(98), 2,
      anon_sym_Sort,
      sym_identifier,
    ACTIONS(96), 9,
      ts_builtin_sym_end,
      anon_sym_COLON_EQ,
      anon_sym_LPAREN,
      anon_sym_EQ_GT,
      anon_sym_DASH_GT,
      anon_sym_POUND,
      sym_def_key,
      sym_thm_key,
      sym_ps_key,
  [1068] = 5,
    ACTIONS(3), 1,
      anon_sym_DASH_DASH,
    ACTIONS(5), 1,
      anon_sym_SLASH_DASH,
    STATE(38), 1,
      sym_comment,
    ACTIONS(78), 2,
      anon_sym_Sort,
      sym_identifier,
    ACTIONS(76), 6,
      anon_sym_COLON,
      anon_sym_LPAREN,
      anon_sym_RPAREN,
      anon_sym_EQ_GT,
      anon_sym_DASH_GT,
      anon_sym_POUND,
  [1090] = 6,
    ACTIONS(3), 1,
      anon_sym_DASH_DASH,
    ACTIONS(5), 1,
      anon_sym_SLASH_DASH,
    ACTIONS(100), 1,
      anon_sym_COLON,
    STATE(39), 1,
      sym_comment,
    ACTIONS(82), 2,
      anon_sym_Sort,
      sym_identifier,
    ACTIONS(80), 5,
      anon_sym_LPAREN,
      anon_sym_RPAREN,
      anon_sym_EQ_GT,
      anon_sym_DASH_GT,
      anon_sym_POUND,
  [1114] = 5,
    ACTIONS(3), 1,
      anon_sym_DASH_DASH,
    ACTIONS(5), 1,
      anon_sym_SLASH_DASH,
    STATE(40), 1,
      sym_comment,
    ACTIONS(86), 2,
      anon_sym_Sort,
      sym_identifier,
    ACTIONS(84), 5,
      anon_sym_LPAREN,
      anon_sym_RPAREN,
      anon_sym_EQ_GT,
      anon_sym_DASH_GT,
      anon_sym_POUND,
  [1135] = 5,
    ACTIONS(3), 1,
      anon_sym_DASH_DASH,
    ACTIONS(5), 1,
      anon_sym_SLASH_DASH,
    STATE(41), 1,
      sym_comment,
    ACTIONS(98), 2,
      anon_sym_Sort,
      sym_identifier,
    ACTIONS(96), 5,
      anon_sym_LPAREN,
      anon_sym_RPAREN,
      anon_sym_EQ_GT,
      anon_sym_DASH_GT,
      anon_sym_POUND,
  [1156] = 5,
    ACTIONS(3), 1,
      anon_sym_DASH_DASH,
    ACTIONS(5), 1,
      anon_sym_SLASH_DASH,
    STATE(42), 1,
      sym_comment,
    ACTIONS(94), 2,
      anon_sym_Sort,
      sym_identifier,
    ACTIONS(92), 5,
      anon_sym_LPAREN,
      anon_sym_RPAREN,
      anon_sym_EQ_GT,
      anon_sym_DASH_GT,
      anon_sym_POUND,
  [1177] = 5,
    ACTIONS(3), 1,
      anon_sym_DASH_DASH,
    ACTIONS(5), 1,
      anon_sym_SLASH_DASH,
    STATE(43), 1,
      sym_comment,
    ACTIONS(82), 2,
      anon_sym_Sort,
      sym_identifier,
    ACTIONS(80), 5,
      anon_sym_LPAREN,
      anon_sym_RPAREN,
      anon_sym_EQ_GT,
      anon_sym_DASH_GT,
      anon_sym_POUND,
  [1198] = 5,
    ACTIONS(3), 1,
      anon_sym_DASH_DASH,
    ACTIONS(5), 1,
      anon_sym_SLASH_DASH,
    STATE(44), 1,
      sym_comment,
    ACTIONS(90), 2,
      anon_sym_Sort,
      sym_identifier,
    ACTIONS(88), 5,
      anon_sym_LPAREN,
      anon_sym_RPAREN,
      anon_sym_EQ_GT,
      anon_sym_DASH_GT,
      anon_sym_POUND,
  [1219] = 6,
    ACTIONS(3), 1,
      anon_sym_DASH_DASH,
    ACTIONS(5), 1,
      anon_sym_SLASH_DASH,
    STATE(45), 1,
      sym_comment,
    STATE(59), 1,
      sym_level,
    ACTIONS(102), 2,
      aux_sym_bound_var_token1,
      sym_identifier,
    ACTIONS(104), 2,
      anon_sym_Max,
      anon_sym_IMax,
  [1240] = 6,
    ACTIONS(3), 1,
      anon_sym_DASH_DASH,
    ACTIONS(5), 1,
      anon_sym_SLASH_DASH,
    STATE(46), 1,
      sym_comment,
    STATE(60), 1,
      sym_level,
    ACTIONS(102), 2,
      aux_sym_bound_var_token1,
      sym_identifier,
    ACTIONS(104), 2,
      anon_sym_Max,
      anon_sym_IMax,
  [1261] = 6,
    ACTIONS(3), 1,
      anon_sym_DASH_DASH,
    ACTIONS(5), 1,
      anon_sym_SLASH_DASH,
    STATE(47), 1,
      sym_comment,
    STATE(58), 1,
      sym_level,
    ACTIONS(102), 2,
      aux_sym_bound_var_token1,
      sym_identifier,
    ACTIONS(104), 2,
      anon_sym_Max,
      anon_sym_IMax,
  [1282] = 5,
    ACTIONS(3), 1,
      anon_sym_DASH_DASH,
    ACTIONS(5), 1,
      anon_sym_SLASH_DASH,
    ACTIONS(106), 1,
      sym_identifier,
    STATE(48), 1,
      sym_comment,
    ACTIONS(47), 4,
      ts_builtin_sym_end,
      sym_def_key,
      sym_thm_key,
      sym_ps_key,
  [1301] = 5,
    ACTIONS(3), 1,
      anon_sym_DASH_DASH,
    ACTIONS(5), 1,
      anon_sym_SLASH_DASH,
    ACTIONS(110), 1,
      sym_identifier,
    STATE(49), 1,
      sym_comment,
    ACTIONS(108), 4,
      ts_builtin_sym_end,
      sym_def_key,
      sym_thm_key,
      sym_ps_key,
  [1320] = 6,
    ACTIONS(3), 1,
      anon_sym_DASH_DASH,
    ACTIONS(5), 1,
      anon_sym_SLASH_DASH,
    STATE(50), 1,
      sym_comment,
    STATE(57), 1,
      sym_level,
    ACTIONS(102), 2,
      aux_sym_bound_var_token1,
      sym_identifier,
    ACTIONS(104), 2,
      anon_sym_Max,
      anon_sym_IMax,
  [1341] = 4,
    ACTIONS(3), 1,
      anon_sym_DASH_DASH,
    ACTIONS(5), 1,
      anon_sym_SLASH_DASH,
    STATE(51), 1,
      sym_comment,
    ACTIONS(112), 4,
      ts_builtin_sym_end,
      sym_def_key,
      sym_thm_key,
      sym_ps_key,
  [1357] = 4,
    ACTIONS(3), 1,
      anon_sym_DASH_DASH,
    ACTIONS(5), 1,
      anon_sym_SLASH_DASH,
    STATE(52), 1,
      sym_comment,
    ACTIONS(47), 4,
      ts_builtin_sym_end,
      sym_def_key,
      sym_thm_key,
      sym_ps_key,
  [1373] = 4,
    ACTIONS(3), 1,
      anon_sym_DASH_DASH,
    ACTIONS(5), 1,
      anon_sym_SLASH_DASH,
    STATE(53), 1,
      sym_comment,
    ACTIONS(114), 3,
      anon_sym_RPAREN,
      anon_sym_PLUS,
      anon_sym_COMMA,
  [1388] = 4,
    ACTIONS(3), 1,
      anon_sym_DASH_DASH,
    ACTIONS(5), 1,
      anon_sym_SLASH_DASH,
    STATE(54), 1,
      sym_comment,
    ACTIONS(116), 3,
      anon_sym_RPAREN,
      anon_sym_PLUS,
      anon_sym_COMMA,
  [1403] = 4,
    ACTIONS(3), 1,
      anon_sym_DASH_DASH,
    ACTIONS(5), 1,
      anon_sym_SLASH_DASH,
    STATE(55), 1,
      sym_comment,
    ACTIONS(118), 3,
      anon_sym_RPAREN,
      anon_sym_PLUS,
      anon_sym_COMMA,
  [1418] = 5,
    ACTIONS(3), 1,
      anon_sym_DASH_DASH,
    ACTIONS(5), 1,
      anon_sym_SLASH_DASH,
    ACTIONS(120), 1,
      anon_sym_EQ_GT,
    ACTIONS(122), 1,
      anon_sym_DASH_GT,
    STATE(56), 1,
      sym_comment,
  [1434] = 5,
    ACTIONS(3), 1,
      anon_sym_DASH_DASH,
    ACTIONS(5), 1,
      anon_sym_SLASH_DASH,
    ACTIONS(124), 1,
      anon_sym_RPAREN,
    ACTIONS(126), 1,
      anon_sym_PLUS,
    STATE(57), 1,
      sym_comment,
  [1450] = 5,
    ACTIONS(3), 1,
      anon_sym_DASH_DASH,
    ACTIONS(5), 1,
      anon_sym_SLASH_DASH,
    ACTIONS(126), 1,
      anon_sym_PLUS,
    ACTIONS(128), 1,
      anon_sym_RPAREN,
    STATE(58), 1,
      sym_comment,
  [1466] = 5,
    ACTIONS(3), 1,
      anon_sym_DASH_DASH,
    ACTIONS(5), 1,
      anon_sym_SLASH_DASH,
    ACTIONS(126), 1,
      anon_sym_PLUS,
    ACTIONS(130), 1,
      anon_sym_COMMA,
    STATE(59), 1,
      sym_comment,
  [1482] = 5,
    ACTIONS(3), 1,
      anon_sym_DASH_DASH,
    ACTIONS(5), 1,
      anon_sym_SLASH_DASH,
    ACTIONS(126), 1,
      anon_sym_PLUS,
    ACTIONS(132), 1,
      anon_sym_RPAREN,
    STATE(60), 1,
      sym_comment,
  [1498] = 5,
    ACTIONS(3), 1,
      anon_sym_DASH_DASH,
    ACTIONS(5), 1,
      anon_sym_SLASH_DASH,
    ACTIONS(134), 1,
      anon_sym_COLON,
    ACTIONS(136), 1,
      anon_sym_COLON_EQ,
    STATE(61), 1,
      sym_comment,
  [1514] = 4,
    ACTIONS(3), 1,
      anon_sym_DASH_DASH,
    ACTIONS(5), 1,
      anon_sym_SLASH_DASH,
    ACTIONS(138), 1,
      anon_sym_COLON,
    STATE(62), 1,
      sym_comment,
  [1527] = 4,
    ACTIONS(3), 1,
      anon_sym_DASH_DASH,
    ACTIONS(5), 1,
      anon_sym_SLASH_DASH,
    ACTIONS(140), 1,
      sym_identifier,
    STATE(63), 1,
      sym_comment,
  [1540] = 4,
    ACTIONS(3), 1,
      anon_sym_DASH_DASH,
    ACTIONS(5), 1,
      anon_sym_SLASH_DASH,
    ACTIONS(142), 1,
      anon_sym_LPAREN,
    STATE(64), 1,
      sym_comment,
  [1553] = 4,
    ACTIONS(3), 1,
      anon_sym_DASH_DASH,
    ACTIONS(5), 1,
      anon_sym_SLASH_DASH,
    ACTIONS(144), 1,
      sym_identifier,
    STATE(65), 1,
      sym_comment,
  [1566] = 4,
    ACTIONS(146), 1,
      anon_sym_DASH_DASH,
    ACTIONS(148), 1,
      anon_sym_SLASH_DASH,
    ACTIONS(150), 1,
      aux_sym_comment_token2,
    STATE(66), 1,
      sym_comment,
  [1579] = 4,
    ACTIONS(3), 1,
      anon_sym_DASH_DASH,
    ACTIONS(5), 1,
      anon_sym_SLASH_DASH,
    ACTIONS(152), 1,
      ts_builtin_sym_end,
    STATE(67), 1,
      sym_comment,
  [1592] = 4,
    ACTIONS(3), 1,
      anon_sym_DASH_DASH,
    ACTIONS(5), 1,
      anon_sym_SLASH_DASH,
    ACTIONS(154), 1,
      anon_sym_LPAREN,
    STATE(68), 1,
      sym_comment,
  [1605] = 4,
    ACTIONS(146), 1,
      anon_sym_DASH_DASH,
    ACTIONS(148), 1,
      anon_sym_SLASH_DASH,
    ACTIONS(156), 1,
      aux_sym_comment_token1,
    STATE(69), 1,
      sym_comment,
  [1618] = 4,
    ACTIONS(3), 1,
      anon_sym_DASH_DASH,
    ACTIONS(5), 1,
      anon_sym_SLASH_DASH,
    ACTIONS(158), 1,
      aux_sym_bound_var_token1,
    STATE(70), 1,
      sym_comment,
  [1631] = 4,
    ACTIONS(3), 1,
      anon_sym_DASH_DASH,
    ACTIONS(5), 1,
      anon_sym_SLASH_DASH,
    ACTIONS(160), 1,
      anon_sym_EQ_GT,
    STATE(71), 1,
      sym_comment,
  [1644] = 4,
    ACTIONS(3), 1,
      anon_sym_DASH_DASH,
    ACTIONS(5), 1,
      anon_sym_SLASH_DASH,
    ACTIONS(162), 1,
      anon_sym_DASH_GT,
    STATE(72), 1,
      sym_comment,
  [1657] = 4,
    ACTIONS(3), 1,
      anon_sym_DASH_DASH,
    ACTIONS(5), 1,
      anon_sym_SLASH_DASH,
    ACTIONS(164), 1,
      anon_sym_EQ_GT,
    STATE(73), 1,
      sym_comment,
  [1670] = 4,
    ACTIONS(3), 1,
      anon_sym_DASH_DASH,
    ACTIONS(5), 1,
      anon_sym_SLASH_DASH,
    ACTIONS(166), 1,
      aux_sym_bound_var_token1,
    STATE(74), 1,
      sym_comment,
  [1683] = 4,
    ACTIONS(3), 1,
      anon_sym_DASH_DASH,
    ACTIONS(5), 1,
      anon_sym_SLASH_DASH,
    ACTIONS(168), 1,
      anon_sym_DASH_GT,
    STATE(75), 1,
      sym_comment,
  [1696] = 4,
    ACTIONS(3), 1,
      anon_sym_DASH_DASH,
    ACTIONS(5), 1,
      anon_sym_SLASH_DASH,
    ACTIONS(170), 1,
      anon_sym_1,
    STATE(76), 1,
      sym_comment,
  [1709] = 4,
    ACTIONS(3), 1,
      anon_sym_DASH_DASH,
    ACTIONS(5), 1,
      anon_sym_SLASH_DASH,
    ACTIONS(172), 1,
      anon_sym_LPAREN,
    STATE(77), 1,
      sym_comment,
  [1722] = 1,
    ACTIONS(174), 1,
      ts_builtin_sym_end,
};

static const uint32_t ts_small_parse_table_map[] = {
  [SMALL_STATE(11)] = 0,
  [SMALL_STATE(12)] = 48,
  [SMALL_STATE(13)] = 99,
  [SMALL_STATE(14)] = 150,
  [SMALL_STATE(15)] = 201,
  [SMALL_STATE(16)] = 240,
  [SMALL_STATE(17)] = 287,
  [SMALL_STATE(18)] = 334,
  [SMALL_STATE(19)] = 376,
  [SMALL_STATE(20)] = 418,
  [SMALL_STATE(21)] = 460,
  [SMALL_STATE(22)] = 502,
  [SMALL_STATE(23)] = 544,
  [SMALL_STATE(24)] = 586,
  [SMALL_STATE(25)] = 628,
  [SMALL_STATE(26)] = 672,
  [SMALL_STATE(27)] = 714,
  [SMALL_STATE(28)] = 756,
  [SMALL_STATE(29)] = 798,
  [SMALL_STATE(30)] = 842,
  [SMALL_STATE(31)] = 881,
  [SMALL_STATE(32)] = 918,
  [SMALL_STATE(33)] = 943,
  [SMALL_STATE(34)] = 968,
  [SMALL_STATE(35)] = 993,
  [SMALL_STATE(36)] = 1018,
  [SMALL_STATE(37)] = 1043,
  [SMALL_STATE(38)] = 1068,
  [SMALL_STATE(39)] = 1090,
  [SMALL_STATE(40)] = 1114,
  [SMALL_STATE(41)] = 1135,
  [SMALL_STATE(42)] = 1156,
  [SMALL_STATE(43)] = 1177,
  [SMALL_STATE(44)] = 1198,
  [SMALL_STATE(45)] = 1219,
  [SMALL_STATE(46)] = 1240,
  [SMALL_STATE(47)] = 1261,
  [SMALL_STATE(48)] = 1282,
  [SMALL_STATE(49)] = 1301,
  [SMALL_STATE(50)] = 1320,
  [SMALL_STATE(51)] = 1341,
  [SMALL_STATE(52)] = 1357,
  [SMALL_STATE(53)] = 1373,
  [SMALL_STATE(54)] = 1388,
  [SMALL_STATE(55)] = 1403,
  [SMALL_STATE(56)] = 1418,
  [SMALL_STATE(57)] = 1434,
  [SMALL_STATE(58)] = 1450,
  [SMALL_STATE(59)] = 1466,
  [SMALL_STATE(60)] = 1482,
  [SMALL_STATE(61)] = 1498,
  [SMALL_STATE(62)] = 1514,
  [SMALL_STATE(63)] = 1527,
  [SMALL_STATE(64)] = 1540,
  [SMALL_STATE(65)] = 1553,
  [SMALL_STATE(66)] = 1566,
  [SMALL_STATE(67)] = 1579,
  [SMALL_STATE(68)] = 1592,
  [SMALL_STATE(69)] = 1605,
  [SMALL_STATE(70)] = 1618,
  [SMALL_STATE(71)] = 1631,
  [SMALL_STATE(72)] = 1644,
  [SMALL_STATE(73)] = 1657,
  [SMALL_STATE(74)] = 1670,
  [SMALL_STATE(75)] = 1683,
  [SMALL_STATE(76)] = 1696,
  [SMALL_STATE(77)] = 1709,
  [SMALL_STATE(78)] = 1722,
};

static const TSParseActionEntry ts_parse_actions[] = {
  [0] = {.entry = {.count = 0, .reusable = false}},
  [1] = {.entry = {.count = 1, .reusable = false}}, RECOVER(),
  [3] = {.entry = {.count = 1, .reusable = true}}, SHIFT(69),
  [5] = {.entry = {.count = 1, .reusable = true}}, SHIFT(66),
  [7] = {.entry = {.count = 1, .reusable = true}}, REDUCE(sym_start, 0, 0, 0),
  [9] = {.entry = {.count = 1, .reusable = true}}, SHIFT(65),
  [11] = {.entry = {.count = 1, .reusable = true}}, SHIFT(63),
  [13] = {.entry = {.count = 1, .reusable = true}}, SHIFT(27),
  [15] = {.entry = {.count = 1, .reusable = true}}, REDUCE(sym_app, 2, 0, 0),
  [17] = {.entry = {.count = 1, .reusable = false}}, REDUCE(sym_app, 2, 0, 0),
  [19] = {.entry = {.count = 1, .reusable = true}}, REDUCE(sym_lambda, 3, 0, 0),
  [21] = {.entry = {.count = 1, .reusable = true}}, SHIFT(25),
  [23] = {.entry = {.count = 1, .reusable = false}}, SHIFT(68),
  [25] = {.entry = {.count = 1, .reusable = true}}, SHIFT(74),
  [27] = {.entry = {.count = 1, .reusable = false}}, SHIFT(32),
  [29] = {.entry = {.count = 1, .reusable = true}}, REDUCE(sym_forall, 3, 0, 0),
  [31] = {.entry = {.count = 1, .reusable = true}}, REDUCE(sym_definition, 4, 0, 0),
  [33] = {.entry = {.count = 1, .reusable = true}}, SHIFT(21),
  [35] = {.entry = {.count = 1, .reusable = true}}, REDUCE(sym_lambda_arg, 1, 0, 0),
  [37] = {.entry = {.count = 1, .reusable = true}}, REDUCE(sym_forall_arg, 1, 0, 0),
  [39] = {.entry = {.count = 1, .reusable = true}}, REDUCE(sym_theorem, 4, 0, 0),
  [41] = {.entry = {.count = 1, .reusable = true}}, REDUCE(sym_proofstep, 2, 0, 0),
  [43] = {.entry = {.count = 1, .reusable = true}}, REDUCE(sym_definition, 6, 0, 0),
  [45] = {.entry = {.count = 1, .reusable = true}}, REDUCE(sym_action, 2, 0, 0),
  [47] = {.entry = {.count = 1, .reusable = true}}, REDUCE(sym_command, 1, 0, 0),
  [49] = {.entry = {.count = 1, .reusable = true}}, SHIFT(29),
  [51] = {.entry = {.count = 1, .reusable = true}}, SHIFT(34),
  [53] = {.entry = {.count = 1, .reusable = false}}, SHIFT(77),
  [55] = {.entry = {.count = 1, .reusable = true}}, SHIFT(70),
  [57] = {.entry = {.count = 1, .reusable = false}}, SHIFT(38),
  [59] = {.entry = {.count = 1, .reusable = true}}, SHIFT(56),
  [61] = {.entry = {.count = 1, .reusable = true}}, SHIFT(40),
  [63] = {.entry = {.count = 1, .reusable = true}}, REDUCE(sym_start, 1, 0, 0),
  [65] = {.entry = {.count = 1, .reusable = true}}, REDUCE(aux_sym_start_repeat1, 2, 0, 0),
  [67] = {.entry = {.count = 2, .reusable = true}}, REDUCE(aux_sym_start_repeat1, 2, 0, 0), SHIFT_REPEAT(65),
  [70] = {.entry = {.count = 2, .reusable = true}}, REDUCE(aux_sym_start_repeat1, 2, 0, 0), SHIFT_REPEAT(63),
  [73] = {.entry = {.count = 2, .reusable = true}}, REDUCE(aux_sym_start_repeat1, 2, 0, 0), SHIFT_REPEAT(27),
  [76] = {.entry = {.count = 1, .reusable = true}}, REDUCE(sym_const, 1, 0, 0),
  [78] = {.entry = {.count = 1, .reusable = false}}, REDUCE(sym_const, 1, 0, 0),
  [80] = {.entry = {.count = 1, .reusable = true}}, REDUCE(sym_primary, 1, 0, 0),
  [82] = {.entry = {.count = 1, .reusable = false}}, REDUCE(sym_primary, 1, 0, 0),
  [84] = {.entry = {.count = 1, .reusable = true}}, REDUCE(sym_expr, 3, 0, 0),
  [86] = {.entry = {.count = 1, .reusable = false}}, REDUCE(sym_expr, 3, 0, 0),
  [88] = {.entry = {.count = 1, .reusable = true}}, REDUCE(sym_sort, 4, 0, 0),
  [90] = {.entry = {.count = 1, .reusable = false}}, REDUCE(sym_sort, 4, 0, 0),
  [92] = {.entry = {.count = 1, .reusable = true}}, REDUCE(sym_bound_var, 2, 0, 0),
  [94] = {.entry = {.count = 1, .reusable = false}}, REDUCE(sym_bound_var, 2, 0, 0),
  [96] = {.entry = {.count = 1, .reusable = true}}, REDUCE(sym_expr, 1, 0, 0),
  [98] = {.entry = {.count = 1, .reusable = false}}, REDUCE(sym_expr, 1, 0, 0),
  [100] = {.entry = {.count = 1, .reusable = true}}, SHIFT(19),
  [102] = {.entry = {.count = 1, .reusable = false}}, SHIFT(55),
  [104] = {.entry = {.count = 1, .reusable = false}}, SHIFT(64),
  [106] = {.entry = {.count = 1, .reusable = false}}, SHIFT(49),
  [108] = {.entry = {.count = 1, .reusable = true}}, REDUCE(sym_search, 2, 0, 0),
  [110] = {.entry = {.count = 1, .reusable = false}}, REDUCE(sym_search, 2, 0, 0),
  [112] = {.entry = {.count = 1, .reusable = true}}, REDUCE(aux_sym_start_repeat1, 1, 0, 0),
  [114] = {.entry = {.count = 1, .reusable = true}}, REDUCE(sym_level, 3, 0, 0),
  [116] = {.entry = {.count = 1, .reusable = true}}, REDUCE(sym_level, 6, 0, 0),
  [118] = {.entry = {.count = 1, .reusable = true}}, REDUCE(sym_level, 1, 0, 0),
  [120] = {.entry = {.count = 1, .reusable = true}}, REDUCE(sym_lambda_arg, 5, 0, 0),
  [122] = {.entry = {.count = 1, .reusable = true}}, REDUCE(sym_forall_arg, 5, 0, 0),
  [124] = {.entry = {.count = 1, .reusable = true}}, SHIFT(35),
  [126] = {.entry = {.count = 1, .reusable = true}}, SHIFT(76),
  [128] = {.entry = {.count = 1, .reusable = true}}, SHIFT(54),
  [130] = {.entry = {.count = 1, .reusable = true}}, SHIFT(47),
  [132] = {.entry = {.count = 1, .reusable = true}}, SHIFT(44),
  [134] = {.entry = {.count = 1, .reusable = false}}, SHIFT(22),
  [136] = {.entry = {.count = 1, .reusable = true}}, SHIFT(20),
  [138] = {.entry = {.count = 1, .reusable = true}}, SHIFT(23),
  [140] = {.entry = {.count = 1, .reusable = true}}, SHIFT(62),
  [142] = {.entry = {.count = 1, .reusable = true}}, SHIFT(45),
  [144] = {.entry = {.count = 1, .reusable = true}}, SHIFT(61),
  [146] = {.entry = {.count = 1, .reusable = false}}, SHIFT(69),
  [148] = {.entry = {.count = 1, .reusable = false}}, SHIFT(66),
  [150] = {.entry = {.count = 1, .reusable = true}}, SHIFT(78),
  [152] = {.entry = {.count = 1, .reusable = true}},  ACCEPT_INPUT(),
  [154] = {.entry = {.count = 1, .reusable = true}}, SHIFT(50),
  [156] = {.entry = {.count = 1, .reusable = false}}, SHIFT(78),
  [158] = {.entry = {.count = 1, .reusable = true}}, SHIFT(42),
  [160] = {.entry = {.count = 1, .reusable = true}}, SHIFT(26),
  [162] = {.entry = {.count = 1, .reusable = true}}, SHIFT(24),
  [164] = {.entry = {.count = 1, .reusable = true}}, SHIFT(18),
  [166] = {.entry = {.count = 1, .reusable = true}}, SHIFT(36),
  [168] = {.entry = {.count = 1, .reusable = true}}, SHIFT(28),
  [170] = {.entry = {.count = 1, .reusable = true}}, SHIFT(53),
  [172] = {.entry = {.count = 1, .reusable = true}}, SHIFT(46),
  [174] = {.entry = {.count = 1, .reusable = true}}, REDUCE(sym_comment, 2, 0, 0),
};

#ifdef __cplusplus
extern "C" {
#endif
#ifdef TREE_SITTER_HIDE_SYMBOLS
#define TS_PUBLIC
#elif defined(_WIN32)
#define TS_PUBLIC __declspec(dllexport)
#else
#define TS_PUBLIC __attribute__((visibility("default")))
#endif

TS_PUBLIC const TSLanguage *tree_sitter_follow(void) {
  static const TSLanguage language = {
    .version = LANGUAGE_VERSION,
    .symbol_count = SYMBOL_COUNT,
    .alias_count = ALIAS_COUNT,
    .token_count = TOKEN_COUNT,
    .external_token_count = EXTERNAL_TOKEN_COUNT,
    .state_count = STATE_COUNT,
    .large_state_count = LARGE_STATE_COUNT,
    .production_id_count = PRODUCTION_ID_COUNT,
    .field_count = FIELD_COUNT,
    .max_alias_sequence_length = MAX_ALIAS_SEQUENCE_LENGTH,
    .parse_table = &ts_parse_table[0][0],
    .small_parse_table = ts_small_parse_table,
    .small_parse_table_map = ts_small_parse_table_map,
    .parse_actions = ts_parse_actions,
    .symbol_names = ts_symbol_names,
    .symbol_metadata = ts_symbol_metadata,
    .public_symbol_map = ts_symbol_map,
    .alias_map = ts_non_terminal_alias_map,
    .alias_sequences = &ts_alias_sequences[0][0],
    .lex_modes = ts_lex_modes,
    .lex_fn = ts_lex,
    .primary_state_ids = ts_primary_state_ids,
  };
  return &language;
}
#ifdef __cplusplus
}
#endif
