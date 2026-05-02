{
  "jest": {
    "testEnvironment": "jsdom",
    "setupFilesAfterEnv": ["<rootDir>/src/setupTests.js"],
    "moduleNameMapper": {
      "\\.(css|less|scss)$": "identity-obj-proxy"
    },
    "transform": {
      "^.+\\.(js|jsx)$": "babel-jest"
    }
  }
}
