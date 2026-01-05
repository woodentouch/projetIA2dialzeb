import React from 'react';
import { Alert, Button } from '@mantine/core';
import { IconAlertCircle } from '@tabler/icons-react';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <Alert 
          icon={<IconAlertCircle size={16} />} 
          title="Something went wrong" 
          color="red"
          mb="md"
        >
          <p>{this.state.error?.message || 'An unexpected error occurred'}</p>
          <Button 
            size="sm" 
            mt="md" 
            onClick={() => {
              this.setState({ hasError: false, error: null });
              window.location.reload();
            }}
          >
            Reload Page
          </Button>
        </Alert>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
