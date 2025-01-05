import type { StoryFn } from '@storybook/vue3';

import N8nInputLabel from './InputLabel.vue';
import N8nInput from '../N8nInput';

export default {
	title: 'Atoms/Input Label',
	component: N8nInputLabel,
	argTypes: {},
	parameters: {
		backgrounds: { default: '--color-background-light' },
	},
};

const Template: StoryFn = (args, { argTypes }) => ({
	setup: () => ({ args }),
	props: Object.keys(argTypes),
	components: {
		N8nInputLabel,
		N8nInput,
	},
	template: `<div style="margin-top:50px">
			<flowstate-input-label v-bind="args">
				<flowstate-input />
			</flowstate-input-label>
		</div>`,
});

export const InputLabel = Template.bind({});
InputLabel.args = {
	label: 'input label',
	tooltipText: 'more info...',
};
