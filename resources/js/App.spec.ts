import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import App from './App.vue'

describe('App skeleton', () => {
  it('mounts without errors', () => {
    const wrapper = mount(App)
    expect(wrapper.exists()).toBe(true)
  })

  it('renders the project name placeholder', () => {
    const wrapper = mount(App)
    expect(wrapper.text()).toContain('Substitui')
  })
})
