import React, { useState } from 'react';

/**
 * ShoppingList Component
 * Manages the shopping list items
 * Allows adding and removing items
 */
const ShoppingList = ({ items, onItemsChange }) => {
  const [newItem, setNewItem] = useState('');

  const handleAddItem = (e) => {
    e.preventDefault();

    if (!newItem.trim()) {
      return; // Don't add empty items
    }

    // Add item (will be normalized when comparing)
    const trimmedItem = newItem.trim();
    if (!items.includes(trimmedItem)) {
      onItemsChange([...items, trimmedItem]);
    }
    setNewItem('');
  };

  const handleRemoveItem = (itemToRemove) => {
    onItemsChange(items.filter(item => item !== itemToRemove));
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleAddItem(e);
    }
  };

  return (
    <div className="shopping-list">
      <h3>Shopping List</h3>

      <form onSubmit={handleAddItem} className="add-item-form">
        <input
          type="text"
          value={newItem}
          onChange={(e) => setNewItem(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Enter item name (e.g., milk, bread)"
          className="item-input"
        />
        <button type="submit" className="add-button">
          Add Item
        </button>
      </form>

      {items.length === 0 ? (
        <p className="empty-message">No items in your shopping list. Add items above.</p>
      ) : (
        <ul className="items-list">
          {items.map((item, index) => (
            <li key={index} className="item">
              <span>{item}</span>
              <button
                onClick={() => handleRemoveItem(item)}
                className="remove-button"
                aria-label={`Remove ${item}`}
              >
                ×
              </button>
            </li>
          ))}
        </ul>
      )}

      {items.length > 0 && (
        <p className="item-count">{items.length} item{items.length !== 1 ? 's' : ''} in list</p>
      )}
    </div>
  );
};

export default ShoppingList;
