module.exports = {
  'env': {
    'browser': true,
    'es6': true,
    'node': true,
  },
  'extends': [
    'eslint:recommended',
    'plugin:react/recommended',
    'plugin:@typescript-eslint/recommended',
    'plugin:@dword-design/import-alias/recommended',
  ],
  'globals': {
    '$': true,
    '$crisp': true,
    'API': true,
    'AccountProvider': true,
    'AccountStore': true,
    'Actions': true,
    'Any': true,
    'AppActions': true,
    'AsyncStorage': true,
    'Button': true,
    'ButtonLink': true,
    'ButtonOutline': true,
    'ButtonProject': true,
    'Chargebee': true,
    'CodeHelp': true,
    'Column': true,
    'Cookies': true,
    'DYNATRACE_URL': true,
    'Dispatcher': true,
    'DYNATRACE_URL': true,
    'dtrum': true,
    'E2E': true,
    'ES6Component': true,
    'FB': true,
    'FeatureListProvider': true,
    'FeatureValue': true,
    'Flex': true,
    'FormGroup': true,
    'Headway': true,
    'IdentityProvider': true,
    'Input': true,
    'InputGroup': true,
    'Link': true,
    'Loader': true,
    'OptionalArray': true,
    'OptionalBool': true,
    'OptionalFunc': true,
    'OptionalNode': true,
    'OptionalNumber': true,
    'OptionalObject': true,
    'OptionalString': true,
    'OrganisationProvider': true,
    'OrganisationSelect': true,
    'Paging': true,
    'Panel': true,
    'PanelSearch': true,
    'Project': true,
    'ProjectProvider': true,
    'Radio': true,
    'React': true,
    'ReactDOM': true,
    'RemoveIcon': true,
    'RequiredElement': true,
    'RequiredFunc': true,
    'RequiredObject': true,
    'RequiredString': true,
    'Row': true,
    'SENTRY_RELEASE_VERSION': true,
    'Select': true,
    'Switch': true,
    'Tooltip': true,
    'Utils': true,
    '_': true,
    '__DEV__': true,
    'closeModal': true,
    'closeModal2': true,
    'delighted': true,
    'describe': true,
    'dtrum': true,
    'em': true,
    'flagsmith': true,
    'ga': true,
    'heap': true,
    'hljs': true,
    'hot': true,
    'isMobile': true,
    'mixpanel': true,
    'moment': true,
    'oneOfType': true,
    'openConfirm': true,
    'openModal': true,
    'openModal2': true,
    'pact': true,
    'projectOverrides': true,
    'propTypes': true,
    'routes': true,
    'testHelpers': true,
    'toast': true,
    'window': true,
    'zE': true,
  },
  'ignorePatterns': [
    'frontend/server/index.js',
    'frontend/next.config.js',
    'frontend/babel.config.js',
  ],
  'parser': '@typescript-eslint/parser',
  'parserOptions': {
    'ecmaFeatures': {
      'legacyDecorators': true,
      'modules': true,
    },
    'ecmaVersion': 6,
    'sourceType': 'module',
  },
  'plugins': [
    'react',
    'react-hooks',
    'sort-keys-fix',
    'sort-destructure-keys',
    '@typescript-eslint',
  ],
  'rules': {
    '@dword-design/import-alias/prefer-alias': [
      'error',
      {
        'alias': {
          'common': './frontend/common/',
          'components': './frontend/web/components/',
          'project': './frontend/web/project/',
        },
      },
    ],
    '@typescript-eslint/ban-ts-comment': 'off',
    '@typescript-eslint/ban-types': 'off',
    '@typescript-eslint/no-empty-function': 'off',
    '@typescript-eslint/no-explicit-any': 'off',
    '@typescript-eslint/no-namespace': 'off',
    '@typescript-eslint/no-var-requires': 'off',
    'default-case': 'error',
    'dot-notation': 'error',
    'guard-for-in': 'error',
    'no-caller': 'error',
    'no-empty': 'off',
    'no-empty-pattern': 'off',
    'no-var': 'error',
    'object-curly-spacing': ['error', 'always'],
    'prefer-template': 'error',
    'react-hooks/exhaustive-deps': 'error',
    'react-hooks/rules-of-hooks': 'error',
    'react/display-name': 'off',
    'react/jsx-no-undef': [
      'error',
      {
        'allowGlobals': true,
      },
    ],
    'react/jsx-uses-react': 'off',
    'react/no-direct-mutation-state': 'off',
    'react/no-find-dom-node': 'off',
    'react/no-string-refs': 'off',
    'react/no-unescaped-entities': 'off',
    'react/prop-types': 'off',
    'react/react-in-jsx-scope': 'off',
    'sort-destructure-keys/sort-destructure-keys': 'warn',
    'sort-keys-fix/sort-keys-fix': 'warn',
    'typescript-eslint/no-empty-interface': 'off',
  },
  'settings': {
    'react': {
      'version': 'detect',
    },
  },
}
