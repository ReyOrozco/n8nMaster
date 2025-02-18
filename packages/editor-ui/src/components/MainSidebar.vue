<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, nextTick, type Ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useBecomeTemplateCreatorStore } from '@/components/BecomeTemplateCreatorCta/becomeTemplateCreatorStore';
import { useCloudPlanStore } from '@/stores/cloudPlan.store';
import { useRootStore } from '@/stores/root.store';
import { useSettingsStore } from '@/stores/settings.store';
import { useTemplatesStore } from '@/stores/templates.store';
import { useUIStore } from '@/stores/ui.store';
import { useUsersStore } from '@/stores/users.store';
import { useVersionsStore } from '@/stores/versions.store';
import { useWorkflowsStore } from '@/stores/workflows.store';

import { hasPermission } from '@/utils/rbac/permissions';
import { useDebounce } from '@/composables/useDebounce';
import { useExternalHooks } from '@/composables/useExternalHooks';
import { useI18n } from '@/composables/useI18n';
import { useTelemetry } from '@/composables/useTelemetry';
import { useUserHelpers } from '@/composables/useUserHelpers';

import { ABOUT_MODAL_KEY, VERSIONS_MODAL_KEY, VIEWS } from '@/constants';
import { useBugReporting } from '@/composables/useBugReporting';
import { usePageRedirectionHelper } from '@/composables/usePageRedirectionHelper';

import { useGlobalEntityCreation } from '@/composables/useGlobalEntityCreation';
import { N8nNavigationDropdown } from 'n8n-design-system';
import { onClickOutside, type VueInstance } from '@vueuse/core';
import Logo from './Logo/Logo.vue';

import dummyImage from '@/assets/image.png';

import { Globe, LogOut } from 'lucide-vue-next';

const becomeTemplateCreatorStore = useBecomeTemplateCreatorStore();
const cloudPlanStore = useCloudPlanStore();
const rootStore = useRootStore();
const settingsStore = useSettingsStore();
const templatesStore = useTemplatesStore();
const uiStore = useUIStore();
const usersStore = useUsersStore();
const versionsStore = useVersionsStore();
const workflowsStore = useWorkflowsStore();

const { callDebounced } = useDebounce();
const externalHooks = useExternalHooks();
const i18n = useI18n();
const route = useRoute();
const router = useRouter();
const telemetry = useTelemetry();
const pageRedirectionHelper = usePageRedirectionHelper();
const { getReportingURL } = useBugReporting();

useUserHelpers(router, route);

// Template refs
const user = ref<Element | null>(null);

// Component data
const basePath = ref('');
const fullyExpanded = ref(false);
const userMenuItems = ref([
	{
		id: 'settings',
		label: i18n.baseText('settings'),
	},
]);

const mainMenuItems = computed(() => [
	{
		id: 'about',
		icon: Globe,
		label: 'Website',
		link: {
			href: 'https://www.google.com/',
			target: '_blank',
		},
		position: 'bottom',
	},
	{
		id: 'telegram',
		icon: Globe,
		label: 'Telegram',
		link: {
			href: 'https://telegram.org/',
			target: '_blank',
		},
		position: 'bottom',
	},
	{
		id: 'x',
		icon: Globe,
		label: 'Twitter/X',
		link: {
			href: 'https://x.com/',
			target: '_blank',
		},
		position: 'bottom',
	},
	{
		id: 'docs',
		icon: Globe,
		label: 'Linkedin',
		link: {
			href: 'https://www.google.com/',
			target: '_blank',
		},
		position: 'bottom',
	},
]);
const createBtn = ref<InstanceType<typeof N8nNavigationDropdown>>();

const isCollapsed = computed(() => uiStore.sidebarMenuCollapsed);

const hasVersionUpdates = computed(
	() => settingsStore.settings.releaseChannel === 'stable' && versionsStore.hasVersionUpdates,
);

const nextVersions = computed(() => versionsStore.nextVersions);
const showUserArea = computed(() => hasPermission(['authenticated']));
const userIsTrialing = computed(() => cloudPlanStore.userIsTrialing);

onMounted(async () => {
	window.addEventListener('resize', onResize);
	basePath.value = rootStore.baseUrl;
	if (user.value) {
		void externalHooks.run('mainSidebar.mounted', {
			userRef: user.value,
		});
	}

	await nextTick(() => {
		uiStore.sidebarMenuCollapsed = window.innerWidth < 900;
		fullyExpanded.value = !isCollapsed.value;
	});

	becomeTemplateCreatorStore.startMonitoringCta();
});

onBeforeUnmount(() => {
	becomeTemplateCreatorStore.stopMonitoringCta();
	window.removeEventListener('resize', onResize);
});

const trackTemplatesClick = () => {
	telemetry.track('User clicked on templates', {
		role: usersStore.currentUserCloudInfo?.role,
		active_workflow_count: workflowsStore.activeWorkflows.length,
	});
};

const trackHelpItemClick = (itemType: string) => {
	telemetry.track('User clicked help resource', {
		type: itemType,
		workflow_id: workflowsStore.workflowId,
	});
};

const onUserActionToggle = (action: string) => {
	switch (action) {
		case 'logout':
			onLogout();
			break;
		case 'settings':
			void router.push({ name: VIEWS.SETTINGS });
			break;
		default:
			break;
	}
};

const onLogout = () => {
	void router.push({ name: VIEWS.SIGNOUT });
};

const toggleCollapse = () => {
	uiStore.toggleSidebarMenuCollapse();
	// When expanding, delay showing some element to ensure smooth animation
	if (!isCollapsed.value) {
		setTimeout(() => {
			fullyExpanded.value = !isCollapsed.value;
		}, 300);
	} else {
		fullyExpanded.value = !isCollapsed.value;
	}
};

const openUpdatesPanel = () => {
	uiStore.openModal(VERSIONS_MODAL_KEY);
};

const handleSelect = (key: string) => {
	switch (key) {
		case 'templates':
			if (settingsStore.isTemplatesEnabled && !templatesStore.hasCustomTemplatesHost) {
				trackTemplatesClick();
			}
			break;
		case 'about': {
			trackHelpItemClick('about');
			uiStore.openModal(ABOUT_MODAL_KEY);
			break;
		}
		case 'cloud-admin': {
			void pageRedirectionHelper.goToDashboard();
			break;
		}
		case 'telegram':
		case 'docs':
		case 'forum':
		case 'examples': {
			trackHelpItemClick(key);
			break;
		}
		default:
			break;
	}
};

const onResize = (event: UIEvent) => {
	void callDebounced(onResizeEnd, { debounceTime: 100 }, event);
};

const onResizeEnd = async (event: UIEvent) => {
	const browserWidth = (event.target as Window).outerWidth;
	await checkWidthAndAdjustSidebar(browserWidth);
};

const checkWidthAndAdjustSidebar = async (width: number) => {
	if (width < 900) {
		uiStore.sidebarMenuCollapsed = true;
		await nextTick();
		fullyExpanded.value = !isCollapsed.value;
	}
};

const {
	menu,
	handleSelect: handleMenuSelect,
	createProjectAppendSlotName,
	projectsLimitReachedMessage,
	upgradeLabel,
} = useGlobalEntityCreation();
onClickOutside(createBtn as Ref<VueInstance>, () => {
	createBtn.value?.close();
});
</script>

<template>
	<div
		id="side-menu"
		:class="{
			['side-menu']: true,
			[$style.sideMenu]: true,
			[$style.sideMenuCollapsed]: isCollapsed,
		}"
	>
		<div
			id="collapse-change-button"
			:class="['clickable', $style.sideMenuCollapseButton]"
			@click="toggleCollapse"
		>
			<N8nIcon v-if="isCollapsed" icon="chevron-right" size="xsmall" class="ml-5xs" />
			<N8nIcon v-else icon="chevron-left" size="xsmall" class="mr-5xs" />
		</div>
		<div :class="$style.logo">
			<Logo
				location="sidebar"
				:collapsed="isCollapsed"
				:release-channel="settingsStore.settings.releaseChannel"
			/>
			<!-- <N8nNavigationDropdown
				ref="createBtn"
				data-test-id="universal-add"
				:menu="menu"
				@select="handleMenuSelect"
			>
				<N8nIconButton icon="plus" type="secondary" outline />
				<template #[createProjectAppendSlotName]="{ item }">
					<N8nTooltip v-if="item.disabled" placement="right" :content="projectsLimitReachedMessage">
						<N8nButton
							:size="'mini'"
							style="margin-left: auto"
							type="tertiary"
							@click="handleMenuSelect(item.id)"
						>
							{{ upgradeLabel }}
						</N8nButton>
					</N8nTooltip>
				</template>
			</N8nNavigationDropdown> -->
		</div>
		<N8nMenu :items="mainMenuItems" :collapsed="isCollapsed" @select="handleSelect">
			<template #header>
				<ProjectNavigation
					:collapsed="isCollapsed"
					:plan-name="cloudPlanStore.currentPlanData?.displayName"
				/>
			</template>

			<template #beforeLowerMenu>
				<BecomeTemplateCreatorCta v-if="fullyExpanded && !userIsTrialing" />
			</template>
			<template #menuSuffix>
				<div>
					<div
						v-if="hasVersionUpdates"
						data-test-id="version-updates-panel-button"
						:class="$style.updates"
						@click="openUpdatesPanel"
					>
						<div :class="$style.giftContainer">
							<GiftNotificationIcon />
						</div>
						<N8nText
							:class="{ ['ml-xs']: true, [$style.expanded]: fullyExpanded }"
							color="text-base"
						>
							{{ nextVersions.length > 99 ? '99+' : nextVersions.length }} update{{
								nextVersions.length > 1 ? 's' : ''
							}}
						</N8nText>
					</div>
					<MainSidebarSourceControl :is-collapsed="isCollapsed" />
				</div>
			</template>
		</N8nMenu>

		<div v-if="showUserArea" :class="$style.footer">
			<div ref="user" :class="$style.userArea">
				<div class="ml-3xs" data-test-id="main-sidebar-user-menu">
					<!-- This dropdown is only enabled when sidebar is collapsed -->
					<ElDropdown placement="right-end" trigger="click" @command="onUserActionToggle">
						<div :class="{ [$style.avatar]: true, ['clickable']: isCollapsed }">
							<N8nAvatar
								:first-name="usersStore.currentUser?.firstName"
								:last-name="usersStore.currentUser?.lastName"
								size="medium"
							/>
						</div>
						<template v-if="isCollapsed" #dropdown>
							<ElDropdownMenu>
								<ElDropdownItem command="settings">
									{{ i18n.baseText('settings') }}
								</ElDropdownItem>
							</ElDropdownMenu>
						</template>
					</ElDropdown>
				</div>
				<div
					:class="{ ['ml-2xs']: true, [$style.userName]: true, [$style.expanded]: fullyExpanded }"
				>
					<N8nText size="small" :bold="true" color="text-dark">{{
						usersStore.currentUser?.fullName
					}}</N8nText>
				</div>
				<div :class="{ [$style.userActions]: true, [$style.expanded]: fullyExpanded }">
					<N8nActionDropdown
						:items="userMenuItems"
						placement="top-start"
						data-test-id="user-menu"
						@select="onUserActionToggle"
					/>
				</div>
			</div>

			<div :class="$style.logout">
				<LogOut />
			</div>
		</div>
	</div>
</template>

<style lang="scss" module>
.sideMenu {
	position: relative;
	height: 100%;
	transition: width 150ms ease-in-out;
	width: $sidebar-expanded-width;

	.logo {
		display: flex;
		align-items: center;
		padding: 10px var(--spacing-xs);
		justify-content: space-between;
		height: 52px;

		background-color: #f7f9fb;
		box-shadow: 0px 0px 3px 0px #0000001f;
		border: 1px solid #e9e9e9;

		margin: 15px 0px 15px 8px;

		img {
			position: relative;
			left: 1px;
			height: 20px;
		}
	}

	&.sideMenuCollapsed {
		width: $sidebar-width;
		padding-top: 100px;

		.logo {
			flex-direction: column;
			gap: 12px;
		}
	}
}

.sideMenuCollapseButton {
	position: absolute;
	right: -10px;
	top: 50%;
	z-index: 999;
	display: flex;
	justify-content: center;
	align-items: center;
	color: var(--color-text-base);
	background-color: var(--color-foreground-xlight);
	width: 20px;
	height: 20px;
	border: var(--border-width-base) var(--border-style-base) var(--color-foreground-base);
	border-radius: 50%;

	&:hover {
		color: var(--color-primary-shade-1);
	}
}

.updates {
	display: flex;
	align-items: center;
	cursor: pointer;
	padding: var(--spacing-2xs) var(--spacing-l);
	margin: var(--spacing-2xs) 0 0;

	svg {
		color: var(--color-text-base) !important;
	}
	span {
		display: none;
		&.expanded {
			display: initial;
		}
	}

	&:hover {
		&,
		& svg {
			color: var(--color-text-dark) !important;
		}
	}
}

.footer {
	height: 52px;
	margin: 15px 0px 15px 8px;
	display: flex;
	gap: 16px;

	.userArea,
	.logout {
		height: 100%;
		border: 1px solid #e9e9e9;
		box-shadow: 0px 0px 3px 0px #0000001f;
		background: #f7f9fb;
		display: flex;
		align-items: center;
	}

	.userArea {
		flex: 1;
		padding: 8px 16px;
	}
	.logout {
		width: 54px;
		justify-content: center;
		cursor: pointer;
	}
}

@media screen and (max-height: 470px) {
	:global(#help) {
		display: none;
	}
}
</style>
