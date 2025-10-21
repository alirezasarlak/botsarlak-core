# 🌌 Bot Routing Map - SarlakBot v3.0

## 📋 Handler Registration Order
```
1. StartHandler
2. OnboardingHandler  
3. MainMenuHandler
4. ProfileHandlerV3
5. AdminHandler
```

## 🎯 Callback Routing Map

### StartHandler Callbacks
| Callback Data | Handler | Method | Description |
|---------------|---------|--------|-------------|
| `start_onboarding` | StartHandler | `start_onboarding_callback` | Start onboarding flow |
| `check_membership` | StartHandler | `check_membership_callback` | Check channel membership |
| `skip_onboarding` | StartHandler | `skip_onboarding_callback` | Skip onboarding |
| `go_home` | StartHandler | `go_home_callback` | Go to main menu |

### OnboardingHandler Callbacks (ConversationHandler)
| Callback Data | Handler | Method | Description |
|---------------|---------|--------|-------------|
| `start_registration` | OnboardingHandler | `start_registration_callback` | Start registration |
| `track_*` | OnboardingHandler | `handle_study_track` | Select study track |
| `grade_band_*` | OnboardingHandler | `handle_grade_band` | Select grade band |
| `grade_year_*` | OnboardingHandler | `handle_grade_year` | Select grade year |
| `phone_*` | OnboardingHandler | `handle_phone_choice` | Phone number choice |
| `back_to_*` | OnboardingHandler | `handle_back_*` | Back navigation |

### MainMenuHandler Callbacks
| Callback Data | Handler | Method | Description |
|---------------|---------|--------|-------------|
| `menu_reports` | MainMenuHandler | `_show_reports_section` | Show reports |
| `menu_profile` | MainMenuHandler | `_show_profile_section` | Show profile section |
| `menu_motivation` | MainMenuHandler | `_show_motivation_section` | Show motivation |
| `menu_competition` | MainMenuHandler | `_show_competition_section` | Show competition |
| `menu_store` | MainMenuHandler | `_show_store_section` | Show store |
| `menu_compass` | MainMenuHandler | `_show_compass_section` | Show compass |
| `menu_settings` | MainMenuHandler | `_show_settings_section` | Show settings |
| `menu_help` | MainMenuHandler | `_show_help_section` | Show help |

### ProfileHandlerV3 Callbacks
| Callback Data | Handler | Method | Description |
|---------------|---------|--------|-------------|
| `profile_view` | ProfileHandlerV3 | `profile_callback` | Show profile details |
| `profile_stats` | ProfileHandlerV3 | `profile_callback` | Show statistics |
| `profile_achievements` | ProfileHandlerV3 | `profile_callback` | Show achievements |
| `profile_badges` | ProfileHandlerV3 | `profile_callback` | Show badges |
| `profile_edit` | ProfileHandlerV3 | `profile_callback` | Edit profile |
| `profile_privacy` | ProfileHandlerV3 | `profile_callback` | Privacy settings |
| `profile_back` | ProfileHandlerV3 | `profile_callback` | Back to main profile |

### AdminHandler Callbacks
| Callback Data | Handler | Method | Description |
|---------------|---------|--------|-------------|
| `admin_*` | AdminHandler | Various | Admin functions |

## 🔄 Flow Diagrams

### Profile Flow
```
User clicks "🪐 پروفایل" in main menu
↓
MainMenuHandler._show_profile_section()
↓
Shows button with callback_data="profile_view"
↓
User clicks "🪐 مشاهده پروفایل"
↓
ProfileHandlerV3.profile_callback() handles "profile_view"
↓
Shows full profile with all buttons
```

### Onboarding Flow
```
User clicks "🚀 شروع سفر"
↓
StartHandler.start_onboarding_callback()
↓
Shows onboarding welcome with buttons
↓
User clicks "🚀 شروع ثبت‌نام"
↓
OnboardingHandler.start_registration_callback()
↓
ConversationHandler manages the flow
```

## ⚠️ Important Notes

1. **No Handler Conflicts**: Each callback data is handled by only one handler
2. **Profile Flow**: MainMenu shows profile section → ProfileHandlerV3 handles profile_* callbacks
3. **Onboarding Flow**: StartHandler delegates to OnboardingHandler for actual onboarding
4. **Database**: All handlers use db_manager for database operations
5. **Error Handling**: All handlers have proper error handling and logging

## 🚨 Common Issues to Avoid

1. **Duplicate Callback Handlers**: Don't register the same callback in multiple handlers
2. **Missing Database Columns**: Always check schema before using new columns
3. **Handler Import Errors**: Ensure all handler classes can be imported
4. **ConversationHandler Conflicts**: Don't mix ConversationHandler with regular CallbackQueryHandler for same patterns
5. **Database Connection Issues**: Always initialize db_manager before use

## 🔧 Maintenance Checklist

- [ ] Run `python scripts/bot_health_check.py` before deployment
- [ ] Check all callback patterns are unique
- [ ] Verify database schema is complete
- [ ] Test all handler imports
- [ ] Verify profile service functionality
- [ ] Check for any handler conflicts
