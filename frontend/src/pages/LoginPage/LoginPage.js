import React from 'react';
import { Button, Card } from 'antd';
import { useNavigate } from 'react-router-dom';

const LoginPage = () => {
  const navigate = useNavigate();
  
  return (
    <Card style={{ width: 400, margin: '100px auto' }}>
      <h2>培正中學環環校部教職員管理系統</h2>
      <Button 
        type="primary" 
        onClick={() => navigate('/application')}
        style={{ marginRight: 10 }}
      >
        新員工申請
      </Button>
      <Button onClick={() => navigate('/login')}>管理層登入</Button>
    </Card>
  );
};

export default LoginPage;