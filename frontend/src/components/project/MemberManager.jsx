import { useState, useEffect } from 'react';
import { Table, Button, Modal, Form, Select, Tag, message, Popconfirm } from 'antd';
import { UserAddOutlined, DeleteOutlined } from '@ant-design/icons';
import projectApi from '../../api/projectApi';

export default function MemberManager({ projectId }) {
  const [members, setMembers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [formOpen, setFormOpen] = useState(false);
  const [form] = Form.useForm();

  const fetchMembers = async () => {
    try {
      const { data } = await projectApi.get(projectId);
      setMembers(data.members || []);
    } catch {
      message.error('Failed to load members');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMembers();
  }, [projectId]);

  const handleAdd = async (values) => {
    try {
      await projectApi.addMember(projectId, values);
      message.success('Member added');
      fetchMembers();
      form.resetFields();
      setFormOpen(false);
    } catch (error) {
      message.error(error.response?.data?.detail || 'Failed to add member');
    }
  };

  const handleRemove = async (userId) => {
    try {
      await projectApi.removeMember(projectId, userId);
      message.success('Member removed');
      fetchMembers();
    } catch (error) {
      message.error(error.response?.data?.detail || 'Failed to remove member');
    }
  };

  const columns = [
    {
      title: 'User ID',
      dataIndex: 'user_id',
      key: 'user_id',
      render: (text) => <span style={{ fontFamily: 'monospace', fontSize: 12 }}>{text.slice(0, 8)}...</span>,
    },
    {
      title: 'Role',
      dataIndex: 'role',
      key: 'role',
      render: (role) => {
        const color = role === 'project_manager' ? 'blue' : role === 'admin' ? 'red' : 'green';
        return <Tag color={color}>{role.replace('_', ' ')}</Tag>;
      },
    },
    {
      title: 'Joined',
      dataIndex: 'joined_at',
      key: 'joined_at',
      render: (date) => new Date(date).toLocaleDateString(),
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_, record) => (
        <Popconfirm title="Remove this member?" onConfirm={() => handleRemove(record.user_id)} okText="Yes" cancelText="No">
          <Button danger size="small" icon={<DeleteOutlined />} />
        </Popconfirm>
      ),
    },
  ];

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <span style={{ fontWeight: 600 }}>Members ({members.length})</span>
        <Button type="primary" icon={<UserAddOutlined />} onClick={() => setFormOpen(true)}>
          Add Member
        </Button>
      </div>
      <Table
        dataSource={members}
        columns={columns}
        rowKey="id"
        loading={loading}
        pagination={false}
        size="small"
      />
      <Modal
        title="Add Member"
        open={formOpen}
        onOk={() => form.submit()}
        onCancel={() => { form.resetFields(); setFormOpen(false); }}
      >
        <Form form={form} layout="vertical" onFinish={handleAdd}>
          <Form.Item name="user_id" label="User ID" rules={[{ required: true, message: 'Enter user ID' }]}>
            <Select
              showSearch
              placeholder="Enter or paste user ID"
              mode="tags"
              maxCount={1}
            />
          </Form.Item>
          <Form.Item name="role" label="Role" initialValue="member">
            <Select>
              <Select.Option value="member">Member</Select.Option>
              <Select.Option value="project_manager">Project Manager</Select.Option>
            </Select>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}