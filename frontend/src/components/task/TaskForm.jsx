import { useState } from 'react';
import { Modal, Form, Input, Select, DatePicker } from 'antd';

export default function TaskForm({ open, onClose, onSubmit, projects, defaultProjectId }) {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);

  const handleOk = async () => {
    try {
      const values = await form.validateFields();
      setLoading(true);
      await onSubmit({
        ...values,
        due_date: values.due_date ? values.due_date.toISOString() : null,
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
      title="New Task"
      open={open}
      onOk={handleOk}
      onCancel={() => { form.resetFields(); onClose(); }}
      confirmLoading={loading}
    >
      <Form form={form} layout="vertical" initialValues={{ priority: 'medium', project_id: defaultProjectId }}>
        {projects && projects.length > 0 && (
          <Form.Item name="project_id" label="Project" rules={[{ required: true, message: 'Select a project' }]}>
            <Select placeholder="Select project">
              {projects.map((p) => (
                <Select.Option key={p.id} value={p.id}>{p.name}</Select.Option>
              ))}
            </Select>
          </Form.Item>
        )}
        <Form.Item name="title" label="Task Title" rules={[{ required: true, message: 'Please enter task title' }]}>
          <Input placeholder="Enter task title" />
        </Form.Item>
        <Form.Item name="description" label="Description">
          <Input.TextArea rows={3} placeholder="Enter description" />
        </Form.Item>
        <Form.Item name="priority" label="Priority">
          <Select>
            <Select.Option value="low">Low</Select.Option>
            <Select.Option value="medium">Medium</Select.Option>
            <Select.Option value="high">High</Select.Option>
            <Select.Option value="critical">Critical</Select.Option>
          </Select>
        </Form.Item>
        <Form.Item name="due_date" label="Due Date">
          <DatePicker style={{ width: '100%' }} />
        </Form.Item>
      </Form>
    </Modal>
  );
}