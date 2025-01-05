import type { StoryFn } from '@storybook/vue3';

import N8nCallout from './Callout.vue';
import N8nLink from '../N8nLink';
import N8nText from '../N8nText';

export default {
	title: 'Atoms/Callout',
	component: N8nCallout,
	argTypes: {
		theme: {
			control: {
				type: 'select',
			},
			options: ['info', 'secondary', 'success', 'warning', 'danger', 'custom'],
		},
		message: {
			control: {
				type: 'text',
			},
		},
		icon: {
			control: {
				type: 'text',
			},
		},
	},
	parameters: {
		design: {
			type: 'figma',
			url: 'https://www.figma.com/file/tPpJvbrnHbP8C496cYuwyW/Node-pinning?node-id=15%3A5777',
		},
	},
};

interface Args {
	theme: string;
	icon: string;
	default: string;
	actions: string;
	trailingContent: string;
}

const template: StoryFn<Args> = (args, { argTypes }) => ({
	setup: () => ({ args }),
	props: Object.keys(argTypes),
	components: {
		N8nLink,
		N8nText,
		N8nCallout,
	},
	template: `
		<flowstate-callout v-bind="args">
			${args.default}
			<template #actions v-if="args.actions">
				${args.actions}
			</template>
			<template #trailingContent v-if="args.trailingContent">
				${args.trailingContent}
			</template>
		</flowstate-callout>
	`,
});

export const defaultCallout = template.bind({});
defaultCallout.args = {
	theme: 'success',
	default: `
		This is a default callout.
	`,
};

export const customCallout = template.bind({});
customCallout.args = {
	theme: 'custom',
	icon: 'code-branch',
	default: `
		This is a custom callout.
	`,
	actions: `
		<flowstate-link size="small">
			Do something!
		</flowstate-link>
	`,
};

export const secondaryCallout = template.bind({});
secondaryCallout.args = {
	theme: 'secondary',
	icon: 'thumbtack',
	default: `
		This data is pinned.
	`,
	actions: `
		<flowstate-link theme="secondary" size="small" :bold="true" :underline="true">
			Unpin
		</flowstate-link>
	`,
	trailingContent: `
		<flowstate-link
			theme="secondary"
			size="small"
			:bold="true"
			:underline="true"
			to="https://flowstate.io"
		>
			Learn more
		</flowstate-link>
	`,
};
