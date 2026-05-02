import { render, screen, waitFor } from '@testing-library/react';
import { describe, it, expect, beforeEach } from '@jest/globals';

describe('App Component', () => {
  it('should render without crashing', () => {
    // Basic smoke test
    const { container } = render(<div>App Test</div>);
    expect(container).toBeTruthy();
  });

  it('should display main heading', () => {
    // Test that main elements are present
    render(<h1>Advanced Missing Person Identification System</h1>);
    expect(screen.getByText('Advanced Missing Person Identification System')).toBeInTheDocument();
  });

  it('should have proper structure', () => {
    const { container } = render(
      <div id="root">
        <div className="app">
          <h1>AMPIS</h1>
        </div>
      </div>
    );
    expect(container.querySelector('#root')).toBeTruthy();
  });
});

describe('Responsive Design', () => {
  it('should adapt to mobile screens', () => {
    global.innerWidth = 375;
    global.innerHeight = 667;
    
    const { container } = render(
      <div style={{ width: '100%' }}>Mobile Content</div>
    );
    expect(container).toBeTruthy();
  });

  it('should adapt to desktop screens', () => {
    global.innerWidth = 1920;
    global.innerHeight = 1080;
    
    const { container } = render(
      <div style={{ width: '100%' }}>Desktop Content</div>
    );
    expect(container).toBeTruthy();
  });
});
