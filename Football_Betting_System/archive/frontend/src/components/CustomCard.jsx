import React from 'react';
import '../styles/CustomCard.css';

export const CustomCard = ({ 
  children, 
  className = '', 
  padding = 'lg',
  shadow = 'sm',
  radius = 'md',
  withBorder = false,
  style = {},
  onClick = null
}) => {
  const paddingClass = {
    'xs': 'custom-card-padding-xs',
    'sm': 'custom-card-padding-sm',
    'md': 'custom-card-padding-md',
    'lg': 'custom-card-padding-lg',
    'xl': 'custom-card-padding-xl'
  }[padding] || 'custom-card-padding-md';

  const shadowClass = {
    'xs': 'custom-card-shadow-xs',
    'sm': 'custom-card-shadow-sm',
    'md': 'custom-card-shadow-md',
    'lg': 'custom-card-shadow-lg',
    'xl': 'custom-card-shadow-xl'
  }[shadow] || 'custom-card-shadow-sm';

  const radiusClass = {
    'xs': 'custom-card-radius-xs',
    'sm': 'custom-card-radius-sm',
    'md': 'custom-card-radius-md',
    'lg': 'custom-card-radius-lg',
    'xl': 'custom-card-radius-xl'
  }[radius] || 'custom-card-radius-md';

  const borderClass = withBorder ? 'custom-card-with-border' : '';

  return (
    <div 
      className={`custom-card ${paddingClass} ${shadowClass} ${radiusClass} ${borderClass} ${className}`}
      style={style}
      onClick={onClick}
    >
      {children}
    </div>
  );
};

export default CustomCard;
