import React, { useState } from 'react';
import { Form, Input, Button, Card, message, DatePicker, Select, Radio } from 'antd';
import { UserOutlined } from '@ant-design/icons';

const { Option } = Select;

const ApplicationPage = () => {
  const [form] = Form.useForm();

  const onFinish = async (values) => {
    try {
      // TODO: 將表單數據發送到後端
      console.log('表單數據：', values);
      message.success('表單提交成功！');
    } catch (error) {
      message.error('提交失敗，請稍後重試！');
    }
  };

  return (
    <div style={{ padding: '24px', maxWidth: '800px', margin: '0 auto' }}>
      <Card 
        title="個人資料 (Personal Information)" 
        bordered={false}
        style={{ 
          boxShadow: '0 1px 2px rgba(0,0,0,0.1)',
          borderRadius: '8px'
        }}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={onFinish}
          initialValues={{
            prefix: '852'
          }}
        >
          {/* 基本信息 */}
          <Form.Item
            name="chineseName"
            label="中文姓名 (Chinese Name)"
            rules={[{ required: true, message: '請輸入中文姓名！' }]}
          >
            <Input placeholder="請輸入中文姓名" />
          </Form.Item>

          <Form.Item
            name="englishName"
            label="英文姓名 (English Name)"
            rules={[{ required: true, message: 'Please input your English name!' }]}
          >
            <Input placeholder="Please input your English name" />
          </Form.Item>

          <Form.Item
            name="idNumber"
            label="身份證號碼 (ID Card Number)"
            rules={[{ required: true, message: '請輸入身份證號碼！' }]}
          >
            <Input placeholder="請輸入身份證號碼" />
          </Form.Item>

          <Form.Item
            name="dateOfBirth"
            label="出生日期 (Date of Birth)"
            rules={[{ required: true, message: '請選擇出生日期！' }]}
          >
            <DatePicker style={{ width: '100%' }} />
          </Form.Item>

          <Form.Item
            name="gender"
            label="性別 (Gender)"
            rules={[{ required: true, message: '請選擇性別！' }]}
          >
            <Radio.Group>
              <Radio value="male">男 (Male)</Radio>
              <Radio value="female">女 (Female)</Radio>
            </Radio.Group>
          </Form.Item>

          <Form.Item
            name="phoneNumber"
            label="手提電話 (Mobile Phone)"
            rules={[{ required: true, message: '請輸入手提電話！' }]}
          >
            <Input
              addonBefore={(
                <Form.Item name="prefix" noStyle>
                  <Select style={{ width: 80 }}>
                    <Option value="852">+852</Option>
                    <Option value="853">+853</Option>
                    <Option value="86">+86</Option>
                  </Select>
                </Form.Item>
              )}
              placeholder="請輸入手提電話號碼"
            />
          </Form.Item>

          <Form.Item
            name="email"
            label="電郵地址 (Email)"
            rules={[
              { required: true, message: '請輸入電郵地址！' },
              { type: 'email', message: '請輸入有效的電郵地址！' }
            ]}
          >
            <Input placeholder="請輸入電郵地址" />
          </Form.Item>

          <Form.Item
            name="address"
            label="住址 (Address)"
            rules={[{ required: true, message: '請輸入住址！' }]}
          >
            <Input.TextArea 
              rows={4} 
              placeholder="請輸入完整住址"
            />
          </Form.Item>

          <Form.Item
            name="maritalStatus"
            label="婚姻狀況 (Marital Status)"
            rules={[{ required: true, message: '請選擇婚姻狀況！' }]}
          >
            <Select placeholder="請選擇婚姻狀況">
              <Option value="single">未婚 (Single)</Option>
              <Option value="married">已婚 (Married)</Option>
              <Option value="divorced">離婚 (Divorced)</Option>
              <Option value="widowed">喪偶 (Widowed)</Option>
            </Select>
          </Form.Item>

          {/* 學歷狀況 (中學及以上) */}
          <Card 
            title="學歷狀況 (中學及以上) (Education Background)" 
            bordered={false}
            style={{ 
              boxShadow: '0 1px 2px rgba(0,0,0,0.1)',
              borderRadius: '8px',
              marginTop: '24px'
            }}
          >
            <Form.List name="education">
              {(fields, { add, remove }) => (
                <>
                  {fields.map(({ key, name, fieldKey, ...restField }) => (
                    <div key={key} style={{ display: 'flex', marginBottom: 8, alignItems: 'center' }}>
                      <Form.Item
                        {...restField}
                        name={[name, 'year']}
                        fieldKey={[fieldKey, 'year']}
                        rules={[{ required: true, message: '請輸入就讀年份！' }]}
                        style={{ flex: 1, marginRight: 8 }}
                      >
                        <Input placeholder="就讀年份 (e.g., 2016-2020)" />
                      </Form.Item>
                      <Form.Item
                        {...restField}
                        name={[name, 'school']}
                        fieldKey={[fieldKey, 'school']}
                        rules={[{ required: true, message: '請輸入就讀學校！' }]}
                        style={{ flex: 2, marginRight: 8 }}
                      >
                        <Input placeholder="就讀學校 (School)" />
                      </Form.Item>
                      <Form.Item
                        {...restField}
                        name={[name, 'degree']}
                        fieldKey={[fieldKey, 'degree']}
                        rules={[{ required: true, message: '請輸入教育程度！' }]}
                        style={{ flex: 1, marginRight: 8 }}
                      >
                        <Input placeholder="教育程度 (Degree)" />
                      </Form.Item>
                      <Form.Item
                        {...restField}
                        name={[name, 'major']}
                        fieldKey={[fieldKey, 'major']}
                        rules={[{ required: true, message: '請輸入專科學位名稱！' }]}
                        style={{ flex: 2, marginRight: 8 }}
                      >
                        <Input placeholder="專科學位名稱 (Major)" />
                      </Form.Item>
                      <Form.Item
                        {...restField}
                        name={[name, 'awardDate']}
                        fieldKey={[fieldKey, 'awardDate']}
                        rules={[{ required: true, message: '請選擇獲得證書日期！' }]}
                        style={{ flex: 1, marginRight: 8 }}
                      >
                        <DatePicker style={{ width: '100%' }} placeholder="獲得證書日期 (Award Date)" />
                      </Form.Item>
                      <Button type="danger" onClick={() => remove(name)}>
                        X
                      </Button>
                    </div>
                  ))}
                  <Form.Item>
                    <Button type="dashed" onClick={() => add()} block icon={<UserOutlined />}>
                      新增學歷 (Add Education)
                    </Button>
                  </Form.Item>
                </>
              )}
            </Form.List>
          </Card>

          <Form.Item>
            <Button type="primary" htmlType="submit" style={{ width: '100%' }}>
              下一步 (Next)
            </Button>
          </Form.Item>
        </Form>
      </Card>
    </div>
  );
};

export default ApplicationPage;