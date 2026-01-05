import React from 'react';
import '../styles/CustomComponents.css';

// Custom Card Component
export const Card = ({ 
  children, 
  className = '', 
  padding = 'lg',
  shadow = 'sm',
  radius = 'md',
  withBorder = false,
  style = {},
  onClick,
}) => {
  const classes = [
    'card',
    `card-padding-${padding}`,
    `card-shadow-${shadow}`,
    `card-radius-${radius}`,
    withBorder ? 'card-border' : '',
    className,
  ].filter(Boolean).join(' ');

  return (
    <div className={classes} style={style} onClick={onClick}>
      {children}
    </div>
  );
};

// Custom Title Component
export const Title = ({ children, order = 1, className = '', mb, mt, style = {} }) => {
  const Tag = `h${order}`;
  const classes = ['title', `title-${order}`, className].filter(Boolean).join(' ');
  const styles = {
    ...style,
    marginBottom: mb ? `${mb * 4}px` : undefined,
    marginTop: mt ? `${mt * 4}px` : undefined,
  };
  
  return <Tag className={classes} style={styles}>{children}</Tag>;
};

// Custom Text Component
export const Text = ({ 
  children, 
  className = '', 
  size = 'md',
  weight,
  color,
  align,
  style = {} 
}) => {
  const classes = [
    'text',
    `text-size-${size}`,
    weight ? `text-weight-${weight}` : '',
    color ? `text-color-${color}` : '',
    align ? `text-align-${align}` : '',
    className,
  ].filter(Boolean).join(' ');

  return <p className={classes} style={style}>{children}</p>;
};

// Custom Badge Component
export const Badge = ({ 
  children, 
  className = '', 
  color = 'blue',
  variant = 'filled',
  size = 'md',
  style = {} 
}) => {
  const classes = [
    'badge',
    `badge-${color}`,
    `badge-${variant}`,
    `badge-size-${size}`,
    className,
  ].filter(Boolean).join(' ');

  return <span className={classes} style={style}>{children}</span>;
};

// Custom Group Component
export const Group = ({ 
  children, 
  className = '', 
  position = 'left',
  spacing = 'md',
  py,
  style = {} 
}) => {
  const classes = [
    'group',
    `group-${position}`,
    `group-spacing-${spacing}`,
    className,
  ].filter(Boolean).join(' ');

  const styles = {
    ...style,
    paddingTop: py ? `${py * 4}px` : undefined,
    paddingBottom: py ? `${py * 4}px` : undefined,
  };

  return <div className={classes} style={styles}>{children}</div>;
};

// Custom Stack Component
export const Stack = ({ 
  children, 
  className = '', 
  spacing = 'md',
  align = 'stretch',
  style = {} 
}) => {
  const classes = [
    'stack',
    `stack-spacing-${spacing}`,
    `stack-align-${align}`,
    className,
  ].filter(Boolean).join(' ');

  return <div className={classes} style={style}>{children}</div>;
};

// Custom Grid Component
export const Grid = ({ children, className = '', style = {} }) => {
  return <div className={`grid ${className}`} style={style}>{children}</div>;
};

export const GridCol = ({ 
  children, 
  className = '', 
  span = 12,
  md,
  lg,
  style = {} 
}) => {
  const classes = [
    'grid-col',
    `grid-span-${span}`,
    md ? `grid-md-${md}` : '',
    lg ? `grid-lg-${lg}` : '',
    className,
  ].filter(Boolean).join(' ');

  return <div className={classes} style={style}>{children}</div>;
};

// Custom Button Component
export const Button = ({ 
  children, 
  className = '', 
  onClick,
  variant = 'filled',
  color = 'blue',
  size = 'md',
  fullWidth = false,
  loading = false,
  disabled = false,
  leftIcon,
  rightIcon,
  style = {} 
}) => {
  const classes = [
    'button',
    `button-${variant}`,
    `button-${color}`,
    `button-size-${size}`,
    fullWidth ? 'button-fullwidth' : '',
    disabled || loading ? 'button-disabled' : '',
    className,
  ].filter(Boolean).join(' ');

  return (
    <button 
      className={classes} 
      onClick={onClick} 
      disabled={disabled || loading}
      style={style}
    >
      {leftIcon && <span className="button-icon-left">{leftIcon}</span>}
      {loading ? 'Loading...' : children}
      {rightIcon && <span className="button-icon-right">{rightIcon}</span>}
    </button>
  );
};

// Custom Loader Component
export const Loader = ({ size = 'md', className = '' }) => {
  const classes = ['loader', `loader-${size}`, className].filter(Boolean).join(' ');
  return <div className={classes}><div className="loader-spinner"></div></div>;
};

// Custom Select Component
export const Select = ({ 
  label,
  placeholder,
  value,
  onChange,
  data = [],
  className = '',
  clearable = false,
  searchable = false,
  style = {}
}) => {
  return (
    <div className={`select-wrapper ${className}`} style={style}>
      {label && <label className="select-label">{label}</label>}
      <select 
        className="select" 
        value={value || ''} 
        onChange={(e) => onChange(e.target.value)}
      >
        <option value="">{placeholder || 'Select...'}</option>
        {data.map((item) => (
          <option key={item.value} value={item.value}>
            {item.label}
          </option>
        ))}
      </select>
    </div>
  );
};

// Custom NumberInput Component
export const NumberInput = ({ 
  label,
  placeholder,
  value,
  onChange,
  min,
  max,
  step = 1,
  className = '',
  style = {}
}) => {
  return (
    <div className={`input-wrapper ${className}`} style={style}>
      {label && <label className="input-label">{label}</label>}
      <input 
        type="number"
        className="input" 
        value={value || ''} 
        onChange={(e) => onChange(parseFloat(e.target.value) || 0)}
        placeholder={placeholder}
        min={min}
        max={max}
        step={step}
      />
    </div>
  );
};

// Custom Progress Component
export const Progress = ({ 
  value = 0,
  color = 'blue',
  size = 'md',
  className = '',
  label,
  style = {}
}) => {
  const classes = [
    'progress',
    `progress-${color}`,
    `progress-size-${size}`,
    className,
  ].filter(Boolean).join(' ');

  return (
    <div className={classes} style={style}>
      <div className="progress-bar" style={{ width: `${value}%` }}>
        {label && <span className="progress-label">{label}</span>}
      </div>
    </div>
  );
};

// Custom Alert Component
export const Alert = ({ 
  children,
  icon,
  title,
  color = 'blue',
  variant = 'filled',
  className = '',
  style = {}
}) => {
  const classes = [
    'alert',
    `alert-${color}`,
    `alert-${variant}`,
    className,
  ].filter(Boolean).join(' ');

  return (
    <div className={classes} style={style}>
      {icon && <div className="alert-icon">{icon}</div>}
      <div className="alert-content">
        {title && <div className="alert-title">{title}</div>}
        <div className="alert-body">{children}</div>
      </div>
    </div>
  );
};

// Custom Table Component
export const Table = ({ children, className = '', style = {} }) => {
  return <table className={`table ${className}`} style={style}>{children}</table>;
};

// Custom Modal Component
export const Modal = ({ 
  opened,
  onClose,
  title,
  children,
  size = 'md',
  className = '',
  style = {}
}) => {
  if (!opened) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div 
        className={`modal modal-${size} ${className}`} 
        style={style}
        onClick={(e) => e.stopPropagation()}
      >
        <div className="modal-header">
          <h3 className="modal-title">{title}</h3>
          <button className="modal-close" onClick={onClose}>×</button>
        </div>
        <div className="modal-body">
          {children}
        </div>
      </div>
    </div>
  );
};
