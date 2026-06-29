import { useState } from 'react';
import { Modal, Form, Input, DatePicker, Select } from 'antd';

export default function ProjectForm({ open, onClose, onSubmit, initialValues }) {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);

  const handleOk = async () => {
    try {
      const values = await form.validateFields();
      setLoading(true);
      await onSubmit({
        ...values,
        deadline: values.deadline ? values.deadline.toISOString() : null,
      });
      form.resetFields();
      onClose();
    } catch {
      // validation error
    } finally {
      setLoading(false);
    }
  };

  return (
    <Modal
      title={initialValues ? 'Edit Project' : 'New Project'}
      open={open}
      onOk={handleOk}
      onCancel={() => { form.resetFields(); onClose(); }}
      confirmLoading={loading}
    >
      <Form form={form} layout="vertical" initialValues={initialValues}>
        <Form.Item name="name" label="Project Name" rules={[{ required: true, message: 'Please enter project name' }]}>
          <Input placeholder="Enter project name" />
        </Form.Item>
        <Form.Item name="description" label="Description">
          <Input.TextArea rows={3} placeholder="Enter description" />
        </Form.Item>
        <Form.Item name="status" label="Status">
          <Select placeholder="Select status">
            <Select.Option value="active">Active</Select.Option>
            <Select.Option value="on_hold">On Hold</Select.Option>
            <Select.Option value="completed">Completed</Select.Option>
            <Select.Option value="archived">Archived</Select.Option>
          </Select>
        </Form.Item>
        <Form.Item name="deadline" label="Deadline">
          <DatePicker style={{ width: '100%' }} />
        </Form.Item>
      </Form>
    </Modal>
  );
}