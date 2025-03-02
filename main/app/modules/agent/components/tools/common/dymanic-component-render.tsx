import React from 'react';

interface ComponentData {
  name: string;
  jsx: string;
  props: any;
  component?: {
    jsx: string;
  };
}

interface DynamicComponentProps {
  component: ComponentData | ComponentData[];
}

const DynamicComponentRender: React.FC<DynamicComponentProps> = ({ component }) => {
  const components = Array.isArray(component) ? component : [component];
  
  return (
    <div className="flex flex-wrap gap-4">
      {components.map((comp, index) => (
        <SingleComponent key={index} component={comp} />
      ))}
    </div>
  );
};

const SingleComponent: React.FC<{ component: ComponentData }> = ({ component }) => {
  if (!component || !component.jsx) {
    return <div>No component data provided</div>;
  }

  // Handle both direct jsx string and nested component structure
  const jsxContent = typeof component.jsx === 'string' 
    ? component.jsx 
    : component.component?.jsx;
    
  if (!jsxContent) {
    return <div>No JSX content found in component</div>;
  }

  try {
    const safeExecute = `
      try {
        const Comp = ${jsxContent}; 
        
        // Validate props before passing them to the component
        const safeProps = props || {};
        
        // Add safety checks for common operations that might cause errors
        const safeFunctions = {
          // Safe substring function that checks if the input is a string
          safeSubstring: (str, ...args) => {
            if (typeof str !== 'string') return '';
            return str.substring(...args);
          }
        };
        
        // Merge safeFunctions with props
        const enhancedProps = { ...safeProps, ...safeFunctions };
        
        return Comp(enhancedProps);
      } catch (err) {
        console.error('Runtime error in dynamic component:', err);
        return React.createElement('div', { className: 'p-4 border border-red-300 bg-red-50 text-red-700 rounded' }, 
          React.createElement('p', {}, 'Error rendering component:'),
          React.createElement('pre', { className: 'mt-2 text-sm' }, String(err))
        );
      }
    `;
    
    const ComponentFunction = new Function(
      'React', 
      'props', 
      safeExecute
    );
    
    return ComponentFunction(React, component.props);
  } catch (error) {
    console.error('Error compiling dynamic component:', error);
    return (
      <div className="p-4 border border-red-300 bg-red-50 text-red-700 rounded">
        <p>Error compiling component</p>
        <pre className="mt-2 text-sm">{String(error)}</pre>
      </div>
    );
  }
};

export default DynamicComponentRender;