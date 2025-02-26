import React from 'react';

interface ComponentData {
  name: string;
  jsx: string;
  props: any;
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

  try {
    const ComponentFunction = new Function(
      'React', 
      'props', 
      `const Comp = ${component.jsx}; return Comp(props);`
    );
    
    return ComponentFunction(React, component.props);
  } catch (error) {
    console.error('Error rendering dynamic component:', error);
    return (
      <div className="error-container">
        <p>Error rendering component</p>
        <pre>{String(error)}</pre>
      </div>
    );
  }
};

export default DynamicComponentRender;