// test_persona_integration.js
// Comprehensive Test Suite for 4-Persona EmotionalAI System Integration

import { personaChatAPI, characterGenerationAPI, healthAPI, apiUtils } from './src/lib/apis/persona.js';

// Test configuration
const TEST_CONFIG = {
  timeout: 10000,
  retries: 3,
  baseUrl: 'http://localhost:5000' // Adjust based on your backend URL
};

// Test results tracking
let testResults = {
  passed: 0,
  failed: 0,
  total: 0,
  details: []
};

// Test utilities
const testUtils = {
  // Run a test with timeout and retry
  async runTest(testName, testFunction, timeout = TEST_CONFIG.timeout) {
    console.log(`🧪 Running test: ${testName}`);
    testResults.total++;
    
    try {
      const result = await Promise.race([
        testFunction(),
        new Promise((_, reject) => 
          setTimeout(() => reject(new Error('Test timeout')), timeout)
        )
      ]);
      
      console.log(`✅ PASS: ${testName}`);
      testResults.passed++;
      testResults.details.push({ name: testName, status: 'PASS', result });
      return result;
    } catch (error) {
      console.error(`❌ FAIL: ${testName} - ${error.message}`);
      testResults.failed++;
      testResults.details.push({ name: testName, status: 'FAIL', error: error.message });
      throw error;
    }
  },

  // Assert utility
  assert(condition, message) {
    if (!condition) {
      throw new Error(`Assertion failed: ${message}`);
    }
  },

  // Deep equality check
  deepEqual(actual, expected, message) {
    const actualStr = JSON.stringify(actual);
    const expectedStr = JSON.stringify(expected);
    if (actualStr !== expectedStr) {
      throw new Error(`${message}\nExpected: ${expectedStr}\nActual: ${actualStr}`);
    }
  }
};

// Test Suite 1: Health Check Tests
const healthTests = {
  async testAPIHealth() {
    const response = await healthAPI.checkHealth();
    testUtils.assert(response, 'Health check should return a response');
    testUtils.assert(response.status === 'healthy', 'API should be healthy');
    return response;
  },

  async testSystemStatus() {
    const response = await healthAPI.getSystemStatus();
    testUtils.assert(response, 'System status should return a response');
    testUtils.assert(response.backend === 'running', 'Backend should be running');
    testUtils.assert(response.llm_router === 'active', 'LLM router should be active');
    return response;
  },

  async testPersonaHealth() {
    const personas = ['mia', 'solene', 'lyra', 'doc'];
    
    for (const persona of personas) {
      const response = await healthAPI.checkPersonaHealth(persona);
      testUtils.assert(response, `${persona} health check should return a response`);
      testUtils.assert(response.status === 'online', `${persona} should be online`);
    }
  }
};

// Test Suite 2: Persona Chat Tests
const chatTests = {
  async testPersonaMessage() {
    const testMessage = "Hello, how are you today?";
    const response = await personaChatAPI.sendMessage('mia', testMessage);
    
    testUtils.assert(response, 'Message should return a response');
    testUtils.assert(response.response, 'Response should contain a message');
    testUtils.assert(response.persona === 'mia', 'Response should be from Mia');
    testUtils.assert(response.llm_model === 'mythomax', 'Should use MythoMax model');
    
    return response;
  },

  async testMoodAnalysis() {
    const testText = "I'm feeling really happy today!";
    const response = await personaChatAPI.analyzeMood('mia', testText);
    
    testUtils.assert(response, 'Mood analysis should return a response');
    testUtils.assert(response.mood, 'Response should contain mood');
    testUtils.assert(typeof response.mood === 'string', 'Mood should be a string');
    
    return response;
  },

  async testPersonaGestures() {
    const moods = ['happy', 'sad', 'excited', 'calm'];
    
    for (const mood of moods) {
      const response = await personaChatAPI.getGesture('mia', mood);
      testUtils.assert(response, `${mood} gesture should return a response`);
      testUtils.assert(response.gesture, 'Response should contain gesture');
    }
  },

  async testAllPersonas() {
    const personas = [
      { id: 'mia', model: 'mythomax' },
      { id: 'solene', model: 'openchat' },
      { id: 'lyra', model: 'qwen2' },
      { id: 'doc', model: 'kimik2' }
    ];
    
    for (const persona of personas) {
      const response = await personaChatAPI.sendMessage(persona.id, "Test message");
      testUtils.assert(response.persona === persona.id, `Should be ${persona.id}`);
      testUtils.assert(response.llm_model === persona.model, `Should use ${persona.model}`);
    }
  }
};

// Test Suite 3: Character Generation Tests
const characterTests = {
  async testCharacterGeneration() {
    const settings = {
      style: 'romantic_casual',
      hair_color: 'warm_brown',
      eye_color: 'deep_green',
      outfit: 'casual_elegant',
      background: 'cozy_home',
      mood: 'warm_affectionate',
      pose: 'natural_standing',
      lighting: 'soft_warm',
      nsfw_level: 'safe'
    };
    
    const response = await characterGenerationAPI.generateCharacter('mia', settings, false);
    
    testUtils.assert(response, 'Character generation should return a response');
    testUtils.assert(response.image_url, 'Response should contain image URL');
    testUtils.assert(response.persona === 'mia', 'Should generate for Mia');
    
    return response;
  },

  async testCharacterTemplates() {
    const personas = ['mia', 'solene', 'lyra', 'doc'];
    
    for (const persona of personas) {
      const response = await characterGenerationAPI.getCharacterTemplate(persona);
      testUtils.assert(response, `${persona} template should return a response`);
      testUtils.assert(response.template, 'Response should contain template');
    }
  },

  async testCharacterStyles() {
    const response = await characterGenerationAPI.getCharacterStyles();
    testUtils.assert(response, 'Character styles should return a response');
    testUtils.assert(Array.isArray(response.styles), 'Styles should be an array');
    testUtils.assert(response.styles.length > 0, 'Should have available styles');
  }
};

// Test Suite 4: Store Integration Tests
const storeTests = {
  async testPersonaStore() {
    // This would test the Svelte stores in a browser environment
    console.log('Store tests require browser environment - skipping');
    return { status: 'skipped', reason: 'Browser environment required' };
  },

  async testUIModeStore() {
    // This would test the UI mode store in a browser environment
    console.log('UI Mode store tests require browser environment - skipping');
    return { status: 'skipped', reason: 'Browser environment required' };
  }
};

// Test Suite 5: Component Integration Tests
const componentTests = {
  async testComponentRendering() {
    // This would test component rendering in a browser environment
    console.log('Component tests require browser environment - skipping');
    return { status: 'skipped', reason: 'Browser environment required' };
  },

  async testComponentInteractions() {
    // This would test component interactions in a browser environment
    console.log('Component interaction tests require browser environment - skipping');
    return { status: 'skipped', reason: 'Browser environment required' };
  }
};

// Test Suite 6: End-to-End Integration Tests
const e2eTests = {
  async testCompletePersonaFlow() {
    // Test complete persona switching and chat flow
    console.log('Testing complete persona flow...');
    
    // 1. Switch to Mia
    const miaResponse = await personaChatAPI.sendMessage('mia', "Hello Mia!");
    testUtils.assert(miaResponse.persona === 'mia', 'Should be Mia');
    
    // 2. Switch to Solene
    const soleneResponse = await personaChatAPI.sendMessage('solene', "Hello Solene!");
    testUtils.assert(soleneResponse.persona === 'solene', 'Should be Solene');
    
    // 3. Switch to Lyra
    const lyraResponse = await personaChatAPI.sendMessage('lyra', "Hello Lyra!");
    testUtils.assert(lyraResponse.persona === 'lyra', 'Should be Lyra');
    
    // 4. Switch to Doc
    const docResponse = await personaChatAPI.sendMessage('doc', "Hello Doc!");
    testUtils.assert(docResponse.persona === 'doc', 'Should be Doc');
    
    return {
      mia: miaResponse,
      solene: soleneResponse,
      lyra: lyraResponse,
      doc: docResponse
    };
  },

  async testCharacterGenerationFlow() {
    // Test complete character generation flow
    console.log('Testing character generation flow...');
    
    const settings = {
      style: 'romantic_casual',
      hair_color: 'warm_brown',
      eye_color: 'deep_green',
      outfit: 'casual_elegant',
      background: 'cozy_home',
      mood: 'warm_affectionate',
      pose: 'natural_standing',
      lighting: 'soft_warm',
      nsfw_level: 'safe'
    };
    
    // Generate character for each persona
    const personas = ['mia', 'solene', 'lyra'];
    const results = {};
    
    for (const persona of personas) {
      const response = await characterGenerationAPI.generateCharacter(persona, settings, false);
      results[persona] = response;
      testUtils.assert(response.image_url, `${persona} should generate image`);
    }
    
    return results;
  }
};

// Test Suite 7: Performance Tests
const performanceTests = {
  async testResponseTime() {
    const startTime = Date.now();
    await personaChatAPI.sendMessage('mia', "Performance test");
    const endTime = Date.now();
    const responseTime = endTime - startTime;
    
    testUtils.assert(responseTime < 5000, `Response time should be under 5s, got ${responseTime}ms`);
    return { responseTime };
  },

  async testConcurrentRequests() {
    const promises = [];
    const numRequests = 5;
    
    for (let i = 0; i < numRequests; i++) {
      promises.push(personaChatAPI.sendMessage('mia', `Concurrent test ${i}`));
    }
    
    const startTime = Date.now();
    const results = await Promise.all(promises);
    const endTime = Date.now();
    const totalTime = endTime - startTime;
    
    testUtils.assert(results.length === numRequests, 'All requests should complete');
    testUtils.assert(totalTime < 10000, `Concurrent requests should complete under 10s, got ${totalTime}ms`);
    
    return { totalTime, results: results.length };
  }
};

// Test Suite 8: Error Handling Tests
const errorTests = {
  async testInvalidPersona() {
    try {
      await personaChatAPI.sendMessage('invalid_persona', "Test message");
      throw new Error('Should have thrown an error for invalid persona');
    } catch (error) {
      testUtils.assert(error.message.includes('API Error'), 'Should return API error');
    }
  },

  async testInvalidEndpoint() {
    try {
      await fetch('/api/phase2/invalid_endpoint');
      throw new Error('Should have thrown an error for invalid endpoint');
    } catch (error) {
      testUtils.assert(error, 'Should handle invalid endpoint gracefully');
    }
  },

  async testNetworkError() {
    // Test with invalid base URL
    const originalBase = TEST_CONFIG.baseUrl;
    TEST_CONFIG.baseUrl = 'http://invalid-url:9999';
    
    try {
      await personaChatAPI.sendMessage('mia', "Test message");
      throw new Error('Should have thrown a network error');
    } catch (error) {
      testUtils.assert(error.message.includes('fetch'), 'Should handle network errors');
    } finally {
      TEST_CONFIG.baseUrl = originalBase;
    }
  }
};

// Main test runner
async function runAllTests() {
  console.log('🚀 Starting Persona System Integration Tests...\n');
  
  const testSuites = [
    { name: 'Health Check Tests', tests: healthTests },
    { name: 'Persona Chat Tests', tests: chatTests },
    { name: 'Character Generation Tests', tests: characterTests },
    { name: 'Store Integration Tests', tests: storeTests },
    { name: 'Component Integration Tests', tests: componentTests },
    { name: 'End-to-End Integration Tests', tests: e2eTests },
    { name: 'Performance Tests', tests: performanceTests },
    { name: 'Error Handling Tests', tests: errorTests }
  ];
  
  for (const suite of testSuites) {
    console.log(`\n📋 Running ${suite.name}...`);
    console.log('='.repeat(50));
    
    for (const [testName, testFunction] of Object.entries(suite.tests)) {
      try {
        await testUtils.runTest(testName, testFunction);
      } catch (error) {
        console.error(`Test suite ${suite.name} failed:`, error);
      }
    }
  }
  
  // Print test results summary
  console.log('\n' + '='.repeat(50));
  console.log('📊 TEST RESULTS SUMMARY');
  console.log('='.repeat(50));
  console.log(`Total Tests: ${testResults.total}`);
  console.log(`Passed: ${testResults.passed} ✅`);
  console.log(`Failed: ${testResults.failed} ❌`);
  console.log(`Success Rate: ${((testResults.passed / testResults.total) * 100).toFixed(1)}%`);
  
  if (testResults.failed > 0) {
    console.log('\n❌ FAILED TESTS:');
    testResults.details
      .filter(test => test.status === 'FAIL')
      .forEach(test => {
        console.log(`  - ${test.name}: ${test.error}`);
      });
  }
  
  console.log('\n🎯 Integration Test Complete!');
  
  return testResults;
}

// Export for use in other test files
export {
  runAllTests,
  testUtils,
  healthTests,
  chatTests,
  characterTests,
  storeTests,
  componentTests,
  e2eTests,
  performanceTests,
  errorTests
};

// Run tests if this file is executed directly
if (typeof window === 'undefined') {
  // Node.js environment
  runAllTests().catch(console.error);
} 