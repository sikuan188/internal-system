import React, { createContext, useState, useContext } from 'react';

const LanguageContext = createContext();

export const useLanguage = () => useContext(LanguageContext);

export const LanguageProvider = ({ children }) => {
  const [language, setLanguage] = useState('zh'); // 默認語言為中文

  const toggleLanguage = () => {
    setLanguage((prevLanguage) => (prevLanguage === 'zh' ? 'en' : 'zh'));
  };

  // 可能還有其他與語言相關的邏輯

  return (
    <LanguageContext.Provider value={{ language, setLanguage, toggleLanguage }}> {/* <--- 添加 toggleLanguage 到 value */}
      {children}
    </LanguageContext.Provider>
  );
};

// 如果您不是這樣導出的，請確保導出的 context value 包含 setLanguage 和 toggleLanguage